from backend.services.kafka import KafkaPublisher


def publish(transaction: dict) -> None:
    publisher = KafkaPublisher()
    publisher.publish_transaction(transaction)
    publisher.flush()
