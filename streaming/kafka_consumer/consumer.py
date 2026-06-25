import json
from json import JSONDecodeError

from confluent_kafka import Consumer, Producer

from backend.config import get_settings
from backend.models.database import SessionLocal, init_database, persist_transaction
from backend.services.alerts import persist_alert, risk_band_from_score
from backend.services.dlq import persist_dead_letter, publish_dead_letter
from compliance.rule_engine.rules import evaluate_rules
from graph.graph_builder.builder import GraphBuilder
from graph.graph_features.features import GraphFeatureService
from llm.explanation_generator.generator import NarrativeGenerator
from ml.ensemble.service import EnsembleScorer
from ml.shap.explainer import explain_features
from streaming.feature_engineering.features import StreamingFeatureEngineer
from streaming.schemas import SchemaValidationError, validate_transaction_message


def run_consumer() -> None:
    settings = get_settings()
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_consumer_group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    features = StreamingFeatureEngineer()
    graph = GraphBuilder()
    graph_features = GraphFeatureService()
    scorer = EnsembleScorer()
    narratives = NarrativeGenerator()
    consumer.subscribe([settings.transactions_topic])
    init_database()
    graph.ensure_schema()
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"kafka error: {msg.error()}")
            continue
        try:
            decoded = json.loads(msg.value())
            txn = validate_transaction_message(decoded)
            with SessionLocal() as session:
                persist_transaction(session, txn)
            base = features.compute(txn)
            graph.upsert_transaction(txn)
            g = graph_features.compute(txn)
            payload = {**base, **g}
            score = scorer.score(payload)
            rule_hits = evaluate_rules(txn, payload)
            explanation = explain_features({**txn, **payload}, float(score["fraud_score"]))
            score_with_band = {
                **score,
                "risk_band": risk_band_from_score(float(score["fraud_score"])),
                "explanation": explanation,
                "narrative": narratives.local_narrative(explanation, g),
            }
            producer.produce(
                settings.features_topic,
                key=txn["account_id"],
                value=json.dumps({**payload, **score_with_band}),
            )
            if score["fraud_score"] >= 0.65 or rule_hits:
                producer.produce(
                    settings.alerts_topic,
                    key=txn["account_id"],
                    value=json.dumps({"transaction": txn, "features": payload, "score": score_with_band}),
                )
                with SessionLocal() as session:
                    persist_alert(session, txn, score_with_band, rule_hits)
            producer.flush(5)
            consumer.commit(message=msg, asynchronous=False)
        except (JSONDecodeError, KeyError, TypeError, SchemaValidationError, ValueError) as exc:
            print(f"skipping invalid transaction message: {exc}")
            with SessionLocal() as session:
                persist_dead_letter(
                    session,
                    {"raw": msg.value().decode("utf-8", errors="replace") if msg.value() else None},
                    str(exc),
                    source_topic=settings.transactions_topic,
                    metadata={
                        "partition": msg.partition(),
                        "offset": msg.offset(),
                        "kind": (
                            "schema_validation_error"
                            if isinstance(exc, SchemaValidationError)
                            else "invalid_message"
                        ),
                        "schema_errors": getattr(exc, "errors", []),
                    },
                )
            publish_dead_letter(
                {"raw": msg.value().decode("utf-8", errors="replace") if msg.value() else None},
                str(exc),
                source_topic=settings.transactions_topic,
            )
            consumer.commit(message=msg, asynchronous=False)
        except Exception as exc:
            producer.flush(5)
            print(f"transaction processing failed; offset not committed: {exc}")
            try:
                failed_payload = json.loads(msg.value()) if msg.value() else {"raw": None}
            except Exception:
                failed_payload = {"raw": msg.value().decode("utf-8", errors="replace") if msg.value() else None}
            with SessionLocal() as session:
                persist_dead_letter(
                    session,
                    failed_payload,
                    str(exc),
                    source_topic=settings.transactions_topic,
                    metadata={"partition": msg.partition(), "offset": msg.offset(), "kind": "processing_error"},
                )
            publish_dead_letter(failed_payload, str(exc), source_topic=settings.transactions_topic)
            consumer.commit(message=msg, asynchronous=False)


if __name__ == "__main__":
    run_consumer()
