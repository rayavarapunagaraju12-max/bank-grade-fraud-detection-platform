import pytest

from streaming.schemas import SchemaValidationError, validate_transaction_message
from streaming.transaction_generator.generator import make_transaction


def test_transaction_schema_accepts_generator_payload() -> None:
    payload = make_transaction(1, fraud_ring=True)

    validated = validate_transaction_message(payload)

    assert validated["transaction_id"] == payload["transaction_id"]
    assert validated["account_id"] == payload["account_id"]
    assert validated["amount"] > 0


def test_transaction_schema_rejects_bad_amount() -> None:
    payload = make_transaction(2)
    payload["amount"] = -10

    with pytest.raises(SchemaValidationError) as exc_info:
        validate_transaction_message(payload)

    assert "schema validation failed" in str(exc_info.value)
    assert exc_info.value.errors
