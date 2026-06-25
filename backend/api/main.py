import random
from typing import Annotated

from fastapi import BackgroundTasks, Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED

from backend.auth.rbac import (
    ROLE_ADMIN,
    ROLE_ANALYST,
    ROLE_AUDITOR,
    ROLE_SUPERVISOR,
    current_identity,
    require_roles,
    seed_default_users,
)
from backend.auth.security import create_access_token, hash_password, verify_bearer_token, verify_password
from backend.config import get_settings
from backend.models.database import (
    AlertRecord,
    ComplianceReportRecord,
    DeadLetterRecord,
    ModelVersionRecord,
    SessionLocal,
    TransactionRecord,
    UserRecord,
    get_session,
    init_database,
    persist_transaction,
)
from backend.schemas.transactions import FeatureVector, FraudScore, TransactionIn
from backend.services.alerts import persist_alert, serialize_alert, transition_alert
from backend.services.kafka import KafkaPublisher
from backend.services.model_governance import register_model_version, serialize_model_version, transition_model
from backend.services.scoring import FraudScoringService
from compliance.audit_logs.audit import verify_audit_chain, write_audit_log
from compliance.reporting.india_str import generate_india_str, validate_india_str
from compliance.rule_engine.rules import evaluate_rules
from compliance.sanctions_screening.screen import SanctionsScreeningService
from compliance.sar_generator.generator import export_sar_xml, generate_sar
from compliance.watchlist_ingestion.service import (
    ingest_demo_feeds,
    ingest_official_feeds,
    ingest_sebi_records,
    ingest_unsc_xml,
    list_watchlist_status,
)
from graph.graph_builder.builder import GraphBuilder
from graph.graph_features.features import GraphFeatureService
from streaming.feature_engineering.features import StreamingFeatureEngineer
from streaming.transaction_generator.generator import make_transaction

settings = get_settings()
app = FastAPI(title="Real-Time Financial Fraud Detection Platform", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

transactions_received = Counter("transactions_received_total", "Transactions received")
publisher = KafkaPublisher()
feature_engineer = StreamingFeatureEngineer()
graph_builder = GraphBuilder()
graph_features = GraphFeatureService()
scoring = FraudScoringService()
sanctions = SanctionsScreeningService()
db_session = Depends(get_session)
identity_dependency = Depends(current_identity)
admin_dependency = Depends(require_roles(ROLE_ADMIN))
analyst_supervisor_admin_dependency = Depends(require_roles(ROLE_ANALYST, ROLE_SUPERVISOR, ROLE_ADMIN))
admin_supervisor_dependency = Depends(require_roles(ROLE_ADMIN, ROLE_SUPERVISOR))
admin_supervisor_auditor_dependency = Depends(require_roles(ROLE_ADMIN, ROLE_SUPERVISOR, ROLE_AUDITOR))
stream_rng = random.SystemRandom()

PUBLIC_PATH_PREFIXES = ("/health", "/metrics", "/docs", "/redoc", "/openapi.json", "/app", "/static")


@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    if request.method == "OPTIONS" or not settings.enable_api_key_auth:
        return await call_next(request)
    if any(request.url.path.startswith(path) for path in PUBLIC_PATH_PREFIXES):
        return await call_next(request)
    api_key = request.headers.get("X-API-Key")
    bearer = request.headers.get("Authorization")
    if api_key != settings.demo_api_key and verify_bearer_token(bearer) is None:
        return Response("Missing or invalid API key", status_code=HTTP_401_UNAUTHORIZED)
    return await call_next(request)


@app.on_event("startup")
def startup() -> None:
    try:
        init_database()
        with SessionLocal() as session:
            seed_default_users(session)
    except Exception as exc:
        print(f"database startup skipped: {exc}")
    try:
        graph_builder.ensure_schema()
    except Exception as exc:
        print(f"graph startup skipped: {exc}")


@app.get("/health")
def health() -> dict:
    kafka_status = (
        "local in-process event mode"
        if publisher.producer is None
        else "connected"
        if publisher.last_error is None
        else publisher.last_error
    )
    return {
        "status": "ok",
        "environment": settings.app_env,
        "mode": "local-realtime" if settings.database_url.startswith("sqlite") else "enterprise-compose",
        "kafka": kafka_status,
        "feature_store": "redis" if feature_engineer.use_redis else "memory",
        "graph": "neo4j" if graph_features.use_neo4j else "memory",
    }


@app.get("/ready")
def ready(session: Session = db_session) -> dict:
    session.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.post("/auth/token")
def issue_demo_token(payload: Annotated[dict, Body(...)]) -> dict:
    username = str(payload.get("username") or "analyst")
    api_key = payload.get("api_key")
    if settings.enable_api_key_auth and api_key != settings.demo_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    with SessionLocal() as session:
        user = session.get(UserRecord, username)
        if user is not None and payload.get("password") is not None:
            if not verify_password(str(payload.get("password")), user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid username or password")
        roles = list(user.roles if user is not None else payload.get("roles") or ["analyst"])
    return {"access_token": create_access_token(username, roles), "token_type": "bearer", "roles": roles}


@app.get("/auth/me")
def me(identity: dict = identity_dependency) -> dict:
    return identity


@app.get("/admin/users")
def list_users(
    session: Session = db_session,
    _: dict = admin_dependency,
) -> list[dict]:
    rows = session.query(UserRecord).order_by(UserRecord.username).all()
    return [
        {"username": row.username, "roles": row.roles, "is_active": bool(row.is_active), "created_at": row.created_at}
        for row in rows
    ]


@app.post("/admin/users")
def upsert_user(
    payload: Annotated[dict, Body(...)],
    session: Session = db_session,
    _: dict = admin_dependency,
) -> dict:
    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "").strip()
    roles = payload.get("roles") or [ROLE_ANALYST]
    allowed = {ROLE_ANALYST, ROLE_SUPERVISOR, ROLE_AUDITOR, ROLE_ADMIN}
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password are required")
    if not isinstance(roles, list) or not set(roles).issubset(allowed):
        raise HTTPException(status_code=400, detail="invalid roles")
    record = UserRecord(
        username=username,
        password_hash=hash_password(password),
        roles=roles,
        is_active=1 if payload.get("is_active", True) else 0,
    )
    session.merge(record)
    session.commit()
    return {"username": username, "roles": roles, "is_active": bool(record.is_active)}


@app.get("/production/readiness")
def production_readiness() -> dict:
    return {
        "positioning": "production-style bank-grade portfolio",
        "client_demo_readiness": "95-100%",
        "pilot_readiness": "80-90%",
        "bank_grade_production_readiness": "65-75%",
        "local_capacity_statement": (
            "Target 100-300 TPS on the i7/16GB laptop demo stack; "
            "validate higher TPS in cloud/staging."
        ),
        "production_config_warnings": settings.production_warnings(),
        "demo_ready": [
            "transaction ingestion",
            "feature engineering",
            "fraud scoring",
            "alert queue",
            "graph context",
            "compliance drafts",
            "audit verification",
        ],
        "bank_grade_controls": [
            "API key and bearer-token guardrails",
            "role-based admin, supervisor, auditor, and analyst access paths",
            "audited alert investigation lifecycle",
            "dead-letter queue capture and controlled replay",
            "Kafka transaction schema validation before publish and consume",
            "Kafka transaction JSON schema contract artifact",
            "model registry with approval and deployment transitions",
            "watchlist ingestion status and official-feed refresh path",
            "Kubernetes CronJob scaffold for official watchlist refresh",
            "Alembic migration baseline and follow-up production-hardening migration",
            "Helm secret references for production credentials",
            "frontend vendor chunk splitting",
            "CI lint, type, security, backend test, model regression, and frontend build workflow",
        ],
        "production_hardening_pending": [
            "managed cloud secrets and secret rotation",
            "formal SSO/OIDC integration",
            "official sanctions feed scheduling and operational monitoring",
            "external Kafka schema registry compatibility gates",
            "cloud load testing",
            "Kubernetes autoscaling and CronJobs validated in a real cluster",
            "formal bank security review and compliance sign-off",
        ],
        "production_style_controls_added": [
            "API key guard",
            "fast scoring response with background side effects",
            "model status endpoint",
            "Redis graph feature cache",
            "Alembic migration baseline",
            "audited alert status workflow",
            "DLQ replay audit trail",
            "laptop-friendly demo compose profile",
            "CI lint/test/build workflow",
        ],
    }


@app.get("/models/status")
def model_status() -> dict:
    return scoring.model_status()


@app.get("/app")
def local_console() -> FileResponse:
    return FileResponse("backend/static/index.html")


@app.post("/transactions", response_model=FraudScore)
async def ingest_transaction(
    transaction: TransactionIn,
    background_tasks: BackgroundTasks,
    session: Session = db_session,
) -> FraudScore:
    payload = transaction.model_dump(mode="json")
    return await process_transaction(payload, session, background_tasks)


async def process_transaction(
    payload: dict,
    session: Session,
    background_tasks: BackgroundTasks | None = None,
) -> FraudScore:
    transactions_received.inc()
    persist_transaction(session, payload)
    publisher.publish_transaction(payload)
    features = feature_engineer.compute(payload)
    graph_payload = graph_features.compute(payload)
    vector = FeatureVector(**features, **graph_payload)
    score = await scoring.score(vector, graph_payload, include_narrative=settings.generate_llm_narrative_inline)
    rule_hits = evaluate_rules(payload, vector.model_dump())
    if background_tasks is None:
        graph_builder.upsert_transaction(payload)
        if score.fraud_score >= 0.65 or rule_hits:
            persist_alert(session, payload, score.model_dump(), rule_hits)
        return score

    background_tasks.add_task(background_update_graph, payload)
    background_tasks.add_task(background_write_decision_audit, payload, score.model_dump(), rule_hits)
    if score.fraud_score >= 0.65 or rule_hits:
        background_tasks.add_task(background_persist_alert, payload, score.model_dump(), rule_hits)
        background_tasks.add_task(background_generate_narrative, score.explanation, graph_payload)
    return score


def background_update_graph(payload: dict) -> None:
    graph_builder.upsert_transaction(payload)


def background_persist_alert(payload: dict, score_data: dict, rule_hits: list) -> None:
    with SessionLocal() as session:
        persist_alert(session, payload, score_data, rule_hits)


def background_write_decision_audit(payload: dict, score_data: dict, rule_hits: list) -> None:
    with SessionLocal() as session:
        write_audit_log(
            session,
            "system",
            "fraud_decision_scored",
            payload["transaction_id"],
            {
                "score": score_data.get("fraud_score"),
                "risk_band": score_data.get("risk_band"),
                "rule_hits": rule_hits,
                "processing": "background_audit",
            },
        )
        session.commit()


async def background_generate_narrative(explanation: dict, graph_payload: dict) -> None:
    await scoring.generate_narrative(explanation, graph_payload)


@app.post("/demo/generate")
async def generate_demo_case(
    fraud_ring: bool = Query(default=True),
    session: Session = db_session,
) -> dict:
    payload = make_transaction(1, fraud_ring=fraud_ring)
    if fraud_ring:
        payload.update(
            {
                "amount": 9250.0,
                "merchant_id": "m_crypto",
                "merchant_category": "crypto",
                "device_id": "device_shared_attack",
                "ip_address": "185.199.10.12",
                "country": "US",
            }
        )
        for i in range(4):
            warmup = make_transaction(i + 100, fraud_ring=True)
            warmup["account_id"] = f"acct_warmup_{i}"
            warmup["device_id"] = payload["device_id"]
            warmup["ip_address"] = payload["ip_address"]
            graph_builder.upsert_transaction(warmup)
            feature_engineer.compute(warmup)
    score = await process_transaction(payload, session)
    if fraud_ring and session.get(AlertRecord, f"alert_{payload['transaction_id']}") is None:
        persist_alert(session, payload, score.model_dump(), ["demo_fraud_ring"])
    return {"transaction": payload, "score": score}


@app.post("/demo/stream/generate")
async def generate_demo_stream(
    count: int = Query(default=1, ge=1, le=25),
    fraud_ratio: float = Query(default=0.35, ge=0, le=1),
    session: Session = db_session,
) -> dict:
    generated = []
    for i in range(count):
        fraud_ring = stream_rng.random() < fraud_ratio
        payload = make_transaction(i, fraud_ring=fraud_ring)
        if fraud_ring:
            payload.update(
                {
                    "amount": max(float(payload["amount"]), 1250.0),
                    "merchant_id": "m_crypto",
                    "merchant_category": "crypto",
                }
            )
        score = await process_transaction(payload, session)
        generated.append({"transaction": payload, "score": score})
    return {"generated": len(generated), "items": generated}


@app.get("/transactions/recent")
def recent_transactions(session: Session = db_session) -> list[dict]:
    rows = session.query(TransactionRecord).order_by(TransactionRecord.created_at.desc()).limit(100).all()
    return [
        {
            "transaction_id": row.transaction_id,
            "account_id": row.account_id,
            "amount": row.amount,
            "payload": row.payload,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.get("/dashboard/summary")
def dashboard_summary(session: Session = db_session) -> dict:
    transactions = session.query(TransactionRecord).order_by(TransactionRecord.created_at.desc()).limit(500).all()
    alerts = session.query(AlertRecord).order_by(AlertRecord.created_at.desc()).limit(500).all()
    scores = [float(alert.score) for alert in alerts]
    total_transactions = session.query(TransactionRecord).count()
    open_alerts = sum(1 for alert in alerts if alert.status == "open")
    avg_risk_score = round(sum(scores) / len(scores) * 100, 1) if scores else 0
    fraud_rate = round((len(alerts) / total_transactions * 100), 2) if total_transactions else 0
    trend = [
        {
            "t": row.created_at.strftime("%H:%M"),
            "score": round(float(row.score) * 100, 1),
            "alerts": 1,
        }
        for row in reversed(alerts[:18])
    ]
    live_transactions = [
        {
            "id": row.transaction_id,
            "amount": row.amount,
            "merchant": row.payload.get("merchant_id", "unknown"),
            "risk_score": next(
                (round(float(alert.score) * 100) for alert in alerts if alert.transaction_id == row.transaction_id),
                0,
            ),
            "status": "flagged" if any(alert.transaction_id == row.transaction_id for alert in alerts) else "approved",
            "timestamp": row.created_at.isoformat(),
        }
        for row in transactions[:25]
    ]
    return {
        "totalTransactions": total_transactions,
        "fraudRate": fraud_rate,
        "avgRiskScore": avg_risk_score,
        "blockedToday": open_alerts,
        "trend": trend,
        "liveTransactions": live_transactions,
    }


@app.get("/alerts")
def list_alerts(
    session: Session = db_session,
    status: str | None = Query(default=None),
    min_score: float = Query(default=0),
    sort: str = Query(default="risk", pattern="^(risk|recent)$"),
) -> list[dict]:
    query = session.query(AlertRecord).filter(AlertRecord.score >= min_score)
    if status:
        query = query.filter(AlertRecord.status == status)
    if sort == "recent":
        query = query.order_by(AlertRecord.created_at.desc(), AlertRecord.score.desc())
    else:
        query = query.order_by(AlertRecord.score.desc(), AlertRecord.created_at.desc())
    return [serialize_alert(row) for row in query.limit(200).all()]


@app.patch("/alerts/{alert_id}/decision")
def decide_alert(
    alert_id: str,
    payload: Annotated[dict | None, Body()] = None,
    decision: str | None = Query(default=None),
    actor: str | None = Query(default=None),
    session: Session = db_session,
    identity: dict = analyst_supervisor_admin_dependency,
) -> dict:
    alert = session.get(AlertRecord, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    payload = payload or {}
    target_status = str(payload.get("status") or decision or "").strip()
    if not target_status:
        raise HTTPException(status_code=400, detail="status is required")
    actor_name = str(payload.get("actor") or actor or identity["sub"])
    try:
        updated = transition_alert(
            session,
            alert,
            target_status,
            actor=actor_name,
            notes=payload.get("notes"),
            assigned_to=payload.get("assigned_to"),
            decision=payload.get("decision"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_alert(updated)


@app.get("/compliance/audit/verify")
def verify_audit(session: Session = db_session) -> dict:
    return verify_audit_chain(session)


@app.post("/compliance/sanctions/screen")
def screen_sanctions(payload: Annotated[dict, Body(...)], session: Session = db_session) -> dict:
    return sanctions.screen(payload.get("name"), payload.get("country"), session=session)


@app.post("/compliance/watchlists/refresh")
def refresh_watchlists(payload: Annotated[dict | None, Body()] = None, session: Session = db_session) -> dict:
    payload = payload or {}
    if not payload:
        result = ingest_demo_feeds(session)
    else:
        result = {"sources": []}
        if payload.get("unsc_xml"):
            result["sources"].append(
                ingest_unsc_xml(session, payload["unsc_xml"], source=payload.get("unsc_source", "UNSC"))
            )
        if payload.get("sebi_records"):
            result["sources"].append(
                ingest_sebi_records(session, payload["sebi_records"], source=payload.get("sebi_source", "SEBI"))
            )
        if not result["sources"]:
            result = ingest_demo_feeds(session)
    write_audit_log(session, "system", "watchlists_refreshed", "watchlists", result)
    session.commit()
    return result


@app.post("/compliance/watchlists/refresh-official")
def refresh_official_watchlists(
    session: Session = db_session,
    _: dict = admin_supervisor_dependency,
) -> dict:
    try:
        result = ingest_official_feeds(session)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Official feed refresh failed: {exc}") from exc
    write_audit_log(session, "system", "official_watchlists_refreshed", "watchlists", result)
    session.commit()
    return result


@app.get("/compliance/watchlists/status")
def watchlist_status(session: Session = db_session) -> dict:
    return list_watchlist_status(session)


@app.get("/dlq/messages")
def list_dead_letters(
    session: Session = db_session,
    status: str | None = Query(default=None),
    _: dict = admin_supervisor_auditor_dependency,
) -> list[dict]:
    query = session.query(DeadLetterRecord)
    if status:
        query = query.filter(DeadLetterRecord.status == status)
    rows = query.order_by(DeadLetterRecord.created_at.desc()).limit(200).all()
    return [
        {
            "event_id": row.event_id,
            "source_topic": row.source_topic,
            "error": row.error,
            "payload": row.payload,
            "metadata": row.metadata_payload,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@app.post("/dlq/messages/{event_id}/retry")
def retry_dead_letter(
    event_id: str,
    session: Session = db_session,
    identity: dict = admin_supervisor_dependency,
) -> dict:
    row = session.get(DeadLetterRecord, event_id)
    if row is None:
        raise HTTPException(status_code=404, detail="DLQ message not found")
    if row.status == "replayed":
        raise HTTPException(status_code=409, detail="DLQ message has already been replayed")
    if not isinstance(row.payload, dict) or "account_id" not in row.payload or "transaction_id" not in row.payload:
        raise HTTPException(status_code=400, detail="DLQ payload is not retryable as a transaction")
    publisher.publish_transaction(row.payload)
    metadata = dict(row.metadata_payload or {})
    metadata["retry_count"] = int(metadata.get("retry_count") or 0) + 1
    metadata["last_replayed_by"] = identity["sub"]
    row.metadata_payload = metadata
    row.status = "replayed"
    write_audit_log(
        session,
        identity["sub"],
        "dlq_message_replayed",
        event_id,
        {"source_topic": row.source_topic, "retry_count": metadata["retry_count"]},
    )
    session.commit()
    return {"event_id": event_id, "status": row.status, "metadata": row.metadata_payload}


@app.get("/models/governance")
def list_model_versions(
    session: Session = db_session,
    _: dict = admin_supervisor_auditor_dependency,
) -> list[dict]:
    rows = session.query(ModelVersionRecord).order_by(ModelVersionRecord.created_at.desc()).limit(100).all()
    return [serialize_model_version(row) for row in rows]


@app.post("/models/governance")
def create_model_version(
    payload: Annotated[dict, Body(...)],
    session: Session = db_session,
    _: dict = admin_supervisor_dependency,
) -> dict:
    try:
        record = register_model_version(session, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_model_version(record)


@app.post("/models/governance/{model_id}/transition")
def transition_model_version(
    model_id: str,
    payload: Annotated[dict, Body(...)],
    session: Session = db_session,
    identity: dict = admin_supervisor_dependency,
) -> dict:
    try:
        record = transition_model(session, model_id, str(payload.get("status") or ""), identity["sub"])
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    write_audit_log(session, identity["sub"], "model_status_changed", model_id, {"status": record.status})
    session.commit()
    return serialize_model_version(record)


@app.post("/compliance/sar")
def create_sar(case: Annotated[dict, Body(...)], session: Session = db_session) -> dict:
    sar = generate_sar(case)
    write_audit_log(session, "system", "sar_draft_created", sar["sar_id"], sar)
    session.commit()
    return sar


@app.post("/compliance/sar/export")
def export_sar(case: Annotated[dict, Body(...)], session: Session = db_session) -> Response:
    sar = generate_sar(case)
    xml = export_sar_xml(sar)
    write_audit_log(session, "system", "sar_xml_exported", sar["sar_id"], sar)
    session.commit()
    return Response(xml, media_type="application/xml")


@app.post("/compliance/reports/india-str")
def create_india_str(case: Annotated[dict, Body(...)], session: Session = db_session) -> dict:
    report = generate_india_str(case)
    validation = validate_india_str(report)
    record = ComplianceReportRecord(
        report_id=report["report_id"],
        report_type=report["report_type"],
        jurisdiction=report["jurisdiction"],
        status="validated" if validation["valid"] else "draft_with_validation_errors",
        subject_account=report["principal_subject"].get("account_id"),
        validation=validation,
        payload=report,
    )
    session.merge(record)
    write_audit_log(session, "system", "india_str_created", report["report_id"], {"validation": validation})
    session.commit()
    return {"report": report, "validation": validation}


@app.post("/compliance/reports/validate")
def validate_compliance_report(report: Annotated[dict, Body(...)]) -> dict:
    if report.get("jurisdiction") == "IN" and report.get("report_type") == "STR":
        return validate_india_str(report)
    errors: list[dict] = [{"path": "report_type", "message": "unsupported report type or jurisdiction"}]
    return {
        "valid": False,
        "errors": errors,
        "warnings": [],
    }


@app.get("/graph/{account_id}")
def account_graph(account_id: str) -> dict:
    return graph_features.subgraph(account_id)


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")
