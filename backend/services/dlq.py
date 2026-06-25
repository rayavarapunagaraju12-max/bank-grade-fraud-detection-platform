from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.models.database import DeadLetterRecord
from backend.services.kafka import KafkaPublisher


def persist_dead_letter(
    session: Session,
    payload: dict,
    error: str,
    source_topic: str = "transactions",
    metadata: dict | None = None,
) -> DeadLetterRecord:
    record = DeadLetterRecord(
        event_id=f"dlq_{uuid4().hex}",
        source_topic=source_topic,
        error=error[:1000],
        payload=payload,
        metadata_payload=metadata or {"captured_at": datetime.now(UTC).isoformat()},
    )
    session.add(record)
    session.commit()
    return record


def publish_dead_letter(payload: dict, error: str, source_topic: str = "transactions") -> None:
    publisher = KafkaPublisher()
    publisher.publish_dead_letter(
        {
            "source_topic": source_topic,
            "error": error[:1000],
            "payload": payload,
            "captured_at": datetime.now(UTC).isoformat(),
        }
    )
    publisher.flush()
