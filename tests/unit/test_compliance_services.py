from compliance.sanctions_screening.screen import SanctionsScreeningService
from compliance.sar_generator.generator import export_sar_xml, generate_sar


def test_sanctions_screening_returns_evidence() -> None:
    result = SanctionsScreeningService().screen("Kim Jong Un", "KP")

    assert result["confidence"] >= 0.8
    assert result["rule_triggered"] in {"SANCTIONS_NAME_MATCH", "HIGH_RISK_COUNTRY"}
    assert result["name_matches"]
    assert result["country_risk"] is True


def test_sar_generation_exports_xml() -> None:
    sar = generate_sar(
        {
            "case_id": "case_001",
            "account_id": "acct_001",
            "customer_name": "Demo Customer",
            "transactions": [{"transaction_id": "txn_001", "account_id": "acct_001", "amount": 12500}],
        }
    )
    xml = export_sar_xml(sar)

    assert sar["status"] == "draft_pending_review"
    assert sar["activity"]["total_amount"] == "12500"
    assert "<BSAReport" in xml
    assert "<SARId>" in xml
