from datetime import UTC, datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.database import AlertRecord
from compliance.audit_logs.audit import write_audit_log

ALERT_STATUS_OPEN = "open"
ALERT_STATUS_INVESTIGATING = "investigating"
ALERT_STATUS_ESCALATED = "escalated"
ALERT_STATUS_CLOSED_FALSE_POSITIVE = "closed_false_positive"
ALERT_STATUS_CLOSED_CONFIRMED_FRAUD = "closed_confirmed_fraud"
ALERT_STATUS_SAR_FILED = "sar_filed"

TERMINAL_ALERT_STATUSES = {
    ALERT_STATUS_CLOSED_FALSE_POSITIVE,
    ALERT_STATUS_CLOSED_CONFIRMED_FRAUD,
    ALERT_STATUS_SAR_FILED,
}

ALLOWED_ALERT_TRANSITIONS = {
    ALERT_STATUS_OPEN: {
        ALERT_STATUS_INVESTIGATING,
        ALERT_STATUS_ESCALATED,
        ALERT_STATUS_CLOSED_FALSE_POSITIVE,
    },
    ALERT_STATUS_INVESTIGATING: {
        ALERT_STATUS_ESCALATED,
        ALERT_STATUS_CLOSED_FALSE_POSITIVE,
        ALERT_STATUS_CLOSED_CONFIRMED_FRAUD,
    },
    ALERT_STATUS_ESCALATED: {
        ALERT_STATUS_INVESTIGATING,
        ALERT_STATUS_CLOSED_FALSE_POSITIVE,
        ALERT_STATUS_CLOSED_CONFIRMED_FRAUD,
        ALERT_STATUS_SAR_FILED,
    },
    ALERT_STATUS_CLOSED_FALSE_POSITIVE: set(),
    ALERT_STATUS_CLOSED_CONFIRMED_FRAUD: {ALERT_STATUS_SAR_FILED},
    ALERT_STATUS_SAR_FILED: set(),
}


def risk_band_from_score(score: float) -> str:
    if score >= 0.85:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def persist_alert(
    session: Session,
    transaction: dict,
    score_payload: dict,
    rule_hits: list[Any] | None = None,
    actor: str = "system",
) -> AlertRecord:
    fraud_score = float(score_payload["fraud_score"])
    risk_band = str(score_payload.get("risk_band") or risk_band_from_score(fraud_score))
    alert_id = f"alert_{transaction['transaction_id']}"
    payload = {
        "transaction": transaction,
        "score": {**score_payload, "risk_band": risk_band},
        "rule_hits": rule_hits or [],
    }
    alert = session.get(AlertRecord, alert_id)
    created = alert is None
    if alert is None:
        alert = AlertRecord(
            alert_id=alert_id,
            transaction_id=transaction["transaction_id"],
            score=fraud_score,
            risk_band=risk_band,
            payload=payload,
        )
        session.add(alert)
    else:
        alert.score = fraud_score
        alert.risk_band = risk_band
        alert.payload = payload
    if created:
        with session.no_autoflush:
            write_audit_log(session, actor, "alert_created", alert.alert_id, alert.payload)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        alert = session.get(AlertRecord, alert_id)
        if alert is None:
            raise
        alert.score = fraud_score
        alert.risk_band = risk_band
        alert.payload = payload
        session.commit()
    return alert


def transition_alert(
    session: Session,
    alert: AlertRecord,
    status: str,
    actor: str,
    notes: str | None = None,
    assigned_to: str | None = None,
    decision: str | None = None,
) -> AlertRecord:
    current_status = alert.status or ALERT_STATUS_OPEN
    target_status = status.strip()
    if target_status not in ALLOWED_ALERT_TRANSITIONS:
        raise ValueError(f"Unsupported alert status: {target_status}")
    if target_status != current_status and target_status not in ALLOWED_ALERT_TRANSITIONS[current_status]:
        raise ValueError(f"Invalid alert transition from {current_status} to {target_status}")

    previous = {
        "status": alert.status,
        "assigned_to": alert.assigned_to,
        "decision": alert.decision,
        "reviewed_by": alert.reviewed_by,
    }
    alert.status = target_status
    if assigned_to is not None:
        alert.assigned_to = assigned_to.strip() or None
    if notes is not None:
        alert.decision_notes = notes.strip() or None
    if decision is not None:
        alert.decision = decision.strip() or None
    if target_status in TERMINAL_ALERT_STATUSES:
        alert.reviewed_by = actor
        alert.resolved_at = datetime.now(UTC)
    alert.updated_at = datetime.now(UTC)

    write_audit_log(
        session,
        actor,
        "alert_status_transitioned",
        alert.alert_id,
        {
            "from": previous,
            "to": {
                "status": alert.status,
                "assigned_to": alert.assigned_to,
                "decision": alert.decision,
                "reviewed_by": alert.reviewed_by,
            },
            "notes": alert.decision_notes,
        },
    )
    session.commit()
    return alert


def serialize_alert(row: AlertRecord) -> dict:
    return {
        "alert_id": row.alert_id,
        "transaction_id": row.transaction_id,
        "score": row.score,
        "risk_band": row.risk_band,
        "status": row.status,
        "assigned_to": row.assigned_to,
        "decision": row.decision,
        "decision_notes": row.decision_notes,
        "reviewed_by": row.reviewed_by,
        "resolved_at": row.resolved_at,
        "payload": row.payload,
        "updated_at": row.updated_at,
        "created_at": row.created_at,
    }
