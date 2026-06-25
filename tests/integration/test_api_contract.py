from fastapi.testclient import TestClient

from backend.api.main import app
from backend.config import get_settings
from backend.models.database import init_database


def make_client() -> TestClient:
    init_database()
    return TestClient(app)


def test_health() -> None:
    client = make_client()
    response = client.get("/health")
    assert response.status_code == 200


def test_readiness_and_model_status() -> None:
    client = make_client()

    readiness = client.get("/production/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["positioning"] == "production-style bank-grade portfolio"
    assert readiness.json()["bank_grade_production_readiness"] == "65-75%"

    model_status = client.get("/models/status")
    assert model_status.status_code == 200
    assert "artifacts" in model_status.json()


def test_api_key_auth_when_enabled() -> None:
    settings = get_settings()
    original_enabled = settings.enable_api_key_auth
    settings.enable_api_key_auth = True
    try:
        client = make_client()

        blocked = client.get("/models/status")
        assert blocked.status_code == 401

        allowed = client.get("/models/status", headers={"X-API-Key": settings.demo_api_key})
        assert allowed.status_code == 200
    finally:
        settings.enable_api_key_auth = original_enabled


def test_sanctions_endpoint() -> None:
    client = make_client()
    response = client.post("/compliance/sanctions/screen", json={"name": "Kim Jong Un", "country": "KP"})

    assert response.status_code == 200
    assert response.json()["confidence"] >= 0.8


def test_sar_export_endpoint() -> None:
    client = make_client()
    response = client.post(
        "/compliance/sar/export",
        json={
            "case_id": "case_001",
            "account_id": "acct_001",
            "transactions": [{"transaction_id": "txn_001", "account_id": "acct_001", "amount": 12500}],
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<BSAReport" in response.text


def test_watchlist_refresh_and_india_str_endpoint() -> None:
    client = make_client()

    refresh = client.post("/compliance/watchlists/refresh", json={})
    assert refresh.status_code == 200
    assert refresh.json()["sources"]

    status = client.get("/compliance/watchlists/status")
    assert status.status_code == 200
    assert status.json()["entries"] >= 1

    report = client.post(
        "/compliance/reports/india-str",
        json={
            "case_id": "case_001",
            "account_id": "acct_001",
            "customer_name": "Demo Customer",
            "pan": "ABCDE1234F",
            "transactions": [{"transaction_id": "txn_001", "account_id": "acct_001", "amount": 150000}],
        },
    )
    assert report.status_code == 200
    assert report.json()["validation"]["valid"] is True
