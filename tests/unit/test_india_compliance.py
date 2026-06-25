from backend.models.database import Base
from compliance.reporting.india_str import generate_india_str, validate_india_str
from compliance.sanctions_screening.screen import SanctionsScreeningService
from compliance.watchlist_ingestion.service import ingest_demo_feeds


def test_demo_watchlists_feed_database_screening(db_session) -> None:
    Base.metadata.create_all(bind=db_session.get_bind())
    result = ingest_demo_feeds(db_session)

    screening = SanctionsScreeningService().screen("North Korea Trading Corp", "KP", session=db_session)

    assert result["sources"][0]["records_loaded"] > 0
    assert screening["confidence"] >= 0.8
    assert screening["name_matches"]
    assert screening["watchlist_mode"] == "database-backed"


def test_india_str_report_validates() -> None:
    report = generate_india_str(
        {
            "case_id": "case_001",
            "account_id": "acct_001",
            "customer_name": "Demo Customer",
            "pan": "ABCDE1234F",
            "risk_score": 0.92,
            "transactions": [{"transaction_id": "txn_001", "account_id": "acct_001", "amount": 150000}],
        }
    )
    validation = validate_india_str(report)

    assert report["jurisdiction"] == "IN"
    assert report["report_type"] == "STR"
    assert validation["valid"] is True
