from pydantic import ValidationError

from backend.schemas.transactions import TransactionIn


class SchemaValidationError(ValueError):
    def __init__(self, message: str, errors: list[dict] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


def validate_transaction_message(payload: dict) -> dict:
    try:
        transaction = TransactionIn.model_validate(payload)
    except ValidationError as exc:
        raise SchemaValidationError("transaction message schema validation failed", exc.errors()) from exc
    return transaction.model_dump(mode="json")
