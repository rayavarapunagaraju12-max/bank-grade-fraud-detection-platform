import hashlib
import json
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.models.database import AuditLogRecord

GENESIS_HASH = "0" * 64


def write_audit_log(session: Session, actor: str, action: str, entity_id: str, payload: dict) -> AuditLogRecord:
    previous_hash = _latest_hash(session)
    event_id = f"audit_{uuid4().hex}"
    created_at = datetime.now(UTC)
    evidence: dict[str, Any] = {
        "evidence": payload,
        "previous_hash": previous_hash,
        "hash_algorithm": "sha256",
    }
    entry_hash = compute_entry_hash(
        event_id=event_id,
        actor=actor,
        action=action,
        entity_id=entity_id,
        payload=cast(dict, evidence["evidence"]),
        previous_hash=previous_hash,
        created_at=created_at.isoformat(),
    )
    evidence["entry_hash"] = entry_hash

    record = AuditLogRecord(
        event_id=event_id,
        actor=actor,
        action=action,
        entity_id=entity_id,
        payload=evidence,
        created_at=created_at,
    )
    session.add(record)
    return record


def verify_audit_chain(session: Session) -> dict:
    previous_hash = GENESIS_HASH
    checked = 0
    failures = []
    rows = session.query(AuditLogRecord).order_by(AuditLogRecord.created_at.asc(), AuditLogRecord.event_id.asc()).all()

    for row in rows:
        payload = row.payload or {}
        evidence = cast(dict, payload.get("evidence", {}))
        expected = compute_entry_hash(
            event_id=row.event_id,
            actor=row.actor,
            action=row.action,
            entity_id=row.entity_id,
            payload=evidence,
            previous_hash=previous_hash,
            created_at=row.created_at.isoformat(),
        )
        if payload.get("previous_hash") != previous_hash or payload.get("entry_hash") != expected:
            failures.append(row.event_id)
        previous_hash = payload.get("entry_hash") or expected
        checked += 1

    return {
        "valid": not failures,
        "checked": checked,
        "failures": failures,
        "latest_hash": previous_hash,
    }


def compute_entry_hash(
    event_id: str,
    actor: str,
    action: str,
    entity_id: str,
    payload: dict,
    previous_hash: str,
    created_at: str,
) -> str:
    canonical = json.dumps(
        {
            "event_id": event_id,
            "actor": actor,
            "action": action,
            "entity_id": entity_id,
            "payload": payload,
            "previous_hash": previous_hash,
            "created_at": created_at,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _latest_hash(session: Session) -> str:
    row = session.query(AuditLogRecord).order_by(AuditLogRecord.created_at.desc()).first()
    if row is None:
        return GENESIS_HASH
    return (row.payload or {}).get("entry_hash", GENESIS_HASH)
