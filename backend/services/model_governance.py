from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.models.database import ModelVersionRecord

ALLOWED_TRANSITIONS = {
    "draft": {"validated", "retired"},
    "validated": {"approved", "retired"},
    "approved": {"deployed", "retired"},
    "deployed": {"retired"},
    "retired": set(),
}


def register_model_version(session: Session, payload: dict) -> ModelVersionRecord:
    model_name = str(payload.get("model_name") or payload.get("name") or "").strip()
    version = str(payload.get("version") or "").strip()
    artifact_path = str(payload.get("artifact_path") or "").strip()
    if not model_name or not version or not artifact_path:
        raise ValueError("model_name, version, and artifact_path are required")
    model_id = str(payload.get("model_id") or f"model_{uuid4().hex}")
    record = ModelVersionRecord(
        model_id=model_id,
        model_name=model_name,
        version=version,
        artifact_path=artifact_path,
        status=str(payload.get("status") or "draft"),
        metrics=payload.get("metrics") or {},
        payload=payload,
    )
    session.merge(record)
    session.commit()
    return record


def transition_model(session: Session, model_id: str, status: str, actor: str) -> ModelVersionRecord:
    record = session.get(ModelVersionRecord, model_id)
    if record is None:
        raise LookupError("Model version not found")
    if status not in ALLOWED_TRANSITIONS.get(record.status, set()):
        raise ValueError(f"Invalid transition from {record.status} to {status}")
    record.status = status
    if status == "approved":
        record.approved_by = actor
        record.approved_at = datetime.now(UTC)
    if status == "deployed":
        retire_deployed_versions(session, record.model_name, keep_model_id=record.model_id)
        record.deployed_at = datetime.now(UTC)
    session.commit()
    return record


def retire_deployed_versions(session: Session, model_name: str, keep_model_id: str) -> None:
    rows = (
        session.query(ModelVersionRecord)
        .filter(ModelVersionRecord.model_name == model_name, ModelVersionRecord.status == "deployed")
        .all()
    )
    for row in rows:
        if row.model_id != keep_model_id:
            row.status = "retired"


def serialize_model_version(record: ModelVersionRecord) -> dict:
    return {
        "model_id": record.model_id,
        "model_name": record.model_name,
        "version": record.version,
        "artifact_path": record.artifact_path,
        "status": record.status,
        "metrics": record.metrics,
        "approved_by": record.approved_by,
        "approved_at": record.approved_at,
        "deployed_at": record.deployed_at,
        "created_at": record.created_at,
    }
