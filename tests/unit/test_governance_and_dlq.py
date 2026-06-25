import pytest

from backend.auth.rbac import seed_default_users
from backend.config import get_settings
from backend.models.database import DeadLetterRecord, UserRecord
from backend.services.alerts import persist_alert, transition_alert
from backend.services.dlq import persist_dead_letter
from backend.services.model_governance import register_model_version, transition_model


def test_seed_default_users(db_session) -> None:
    seed_default_users(db_session)

    admin = db_session.get(UserRecord, "admin")
    assert admin is not None
    assert "admin" in admin.roles


def test_dead_letter_persistence(db_session) -> None:
    record = persist_dead_letter(
        db_session,
        {"transaction_id": "txn_001", "account_id": "acct_001"},
        "boom",
        metadata={"partition": 0, "offset": 1},
    )

    stored = db_session.get(DeadLetterRecord, record.event_id)
    assert stored is not None
    assert stored.status == "open"
    assert stored.metadata_payload["offset"] == 1


def test_alert_workflow_records_reviewer_and_rejects_invalid_transition(db_session) -> None:
    alert = persist_alert(
        db_session,
        {"transaction_id": "txn_alert_001", "account_id": "acct_001", "amount": 9200},
        {"fraud_score": 0.91, "risk_band": "critical"},
        ["high_risk_amount"],
    )

    investigating = transition_alert(
        db_session,
        alert,
        "investigating",
        actor="analyst",
        assigned_to="analyst",
        notes="Reviewing account velocity and device reuse",
    )
    assert investigating.status == "investigating"
    assert investigating.assigned_to == "analyst"

    closed = transition_alert(
        db_session,
        investigating,
        "closed_confirmed_fraud",
        actor="supervisor",
        decision="confirmed_fraud",
        notes="Confirmed synthetic fraud ring indicators",
    )
    assert closed.reviewed_by == "supervisor"
    assert closed.resolved_at is not None

    with pytest.raises(ValueError):
        transition_alert(db_session, closed, "open", actor="analyst")


def test_model_governance_transitions(db_session) -> None:
    model = register_model_version(
        db_session,
        {
            "model_name": "xgboost",
            "version": "2026.06.18",
            "artifact_path": "training/model_registry/xgboost.joblib",
            "metrics": {"auc": 0.91},
        },
    )

    assert model.status == "draft"
    transition_model(db_session, model.model_id, "validated", "supervisor")
    transition_model(db_session, model.model_id, "approved", "supervisor")
    deployed = transition_model(db_session, model.model_id, "deployed", "supervisor")

    assert deployed.status == "deployed"
    assert deployed.approved_by == "supervisor"


def test_model_governance_rejects_invalid_transition(db_session) -> None:
    model = register_model_version(
        db_session,
        {
            "model_name": "isolation_forest",
            "version": "v1",
            "artifact_path": "training/model_registry/isolation_forest.joblib",
        },
    )

    with pytest.raises(ValueError):
        transition_model(db_session, model.model_id, "deployed", "supervisor")


def test_production_warnings_flag_demo_secrets() -> None:
    settings = get_settings()
    original_env = settings.app_env
    original_jwt_secret = settings.jwt_secret
    original_database_url = settings.database_url
    try:
        settings.app_env = "production"
        settings.jwt_secret = "change-me-in-production"
        settings.database_url = "postgresql+psycopg://fraud:fraud_password@localhost:5432/fraud"
        warnings = settings.production_warnings()
    finally:
        settings.app_env = original_env
        settings.jwt_secret = original_jwt_secret
        settings.database_url = original_database_url

    assert any("JWT_SECRET" in warning for warning in warnings)
    assert any("demo database password" in warning for warning in warnings)
