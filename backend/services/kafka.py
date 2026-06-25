import json

from confluent_kafka import Producer

from backend.config import get_settings
from streaming.schemas import validate_transaction_message


class KafkaPublisher:
    def __init__(self) -> None:
        settings = get_settings()
        self.topic = settings.transactions_topic
        self.dlq_topic = settings.dlq_topic
        self.producer = (
            Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
            if settings.kafka_enabled
            else None
        )
        self.last_error: str | None = None

    def publish_transaction(self, transaction: dict) -> None:
        validated = validate_transaction_message(transaction)
        self._publish(self.topic, validated, validated["account_id"])

    def publish_dead_letter(self, event: dict) -> None:
        key = str(event.get("source_topic") or "dlq")
        self._publish(self.dlq_topic, event, key)

    def _publish(self, topic: str, payload: dict, key: str) -> None:
        if self.producer is None:
            self.last_error = "local in-process event mode"
            return
        try:
            self.producer.produce(
                topic,
                key=key.encode("utf-8"),
                value=json.dumps(payload, default=str).encode("utf-8"),
            )
            self.producer.poll(0)
            self.last_error = None
        except Exception as exc:
            self.last_error = str(exc)

    def flush(self) -> None:
        if self.producer is None:
            return
        try:
            self.producer.flush(2)
        except Exception as exc:
            self.last_error = str(exc)
