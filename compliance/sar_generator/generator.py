from datetime import UTC, datetime
from decimal import Decimal

# XML is generated for export here, not parsed from input.
from xml.etree.ElementTree import Element, SubElement, tostring  # nosec B405


def generate_sar(case: dict) -> dict:
    created_at = datetime.now(UTC)
    transactions = case.get("transactions", [])
    total_amount = sum((Decimal(str(txn.get("amount", 0))) for txn in transactions), Decimal("0"))
    subject = _subject_from_case(case)
    activity = _activity_from_case(case, total_amount)

    return {
        "sar_id": f"SAR-{created_at.strftime('%Y%m%d%H%M%S')}",
        "status": "draft_pending_review",
        "created_at": created_at.isoformat(),
        "filing_institution": {
            "name": case.get("institution_name", "Demo Financial Institution"),
            "internal_case_id": case.get("case_id"),
        },
        "subject": subject,
        "activity": activity,
        "transactions": transactions,
        "narrative": _narrative(case, subject, activity),
        "review": {
            "prepared_by": case.get("prepared_by", "system"),
            "requires_human_approval": True,
            "export_format": "FinCEN_BSA_XML_DEMO",
        },
    }


def export_sar_xml(sar: dict) -> str:
    root = Element("BSAReport", attrib={"type": "SAR", "format": "demo-fincen-bsa"})
    filing = SubElement(root, "FilingInformation")
    _add_text(filing, "SARId", sar["sar_id"])
    _add_text(filing, "Status", sar["status"])
    _add_text(filing, "CreatedAt", sar["created_at"])
    _add_text(filing, "InstitutionName", sar["filing_institution"]["name"])
    _add_text(filing, "InternalCaseId", sar["filing_institution"].get("internal_case_id"))

    subject = SubElement(root, "Subject")
    for key, value in sar["subject"].items():
        _add_text(subject, _xml_name(key), value)

    activity = SubElement(root, "SuspiciousActivity")
    for key, value in sar["activity"].items():
        _add_text(activity, _xml_name(key), value)

    transactions_node = SubElement(root, "Transactions")
    for txn in sar.get("transactions", []):
        txn_node = SubElement(transactions_node, "Transaction")
        for key in ("transaction_id", "account_id", "amount", "currency", "channel", "merchant_id", "timestamp"):
            _add_text(txn_node, _xml_name(key), txn.get(key))

    _add_text(root, "Narrative", sar.get("narrative"))
    return tostring(root, encoding="unicode")


def _subject_from_case(case: dict) -> dict:
    return {
        "account_id": case.get("account_id") or case.get("subject_account"),
        "customer_name": case.get("customer_name", "Unknown customer"),
        "beneficiary_id": case.get("beneficiary_id"),
        "country": case.get("country", "US"),
    }


def _activity_from_case(case: dict, total_amount: Decimal) -> dict:
    return {
        "activity_type": case.get("activity_type", "suspected_fraud"),
        "risk_score": case.get("risk_score"),
        "total_amount": str(total_amount),
        "reason": case.get("reason", "Multiple fraud indicators exceeded review threshold."),
        "date_range": case.get("date_range", "see transaction timestamps"),
    }


def _narrative(case: dict, subject: dict, activity: dict) -> str:
    if case.get("narrative"):
        return str(case["narrative"])
    return (
        f"Account {subject.get('account_id')} was flagged for {activity.get('activity_type')} "
        f"with total suspicious activity of {activity.get('total_amount')}. "
        f"Primary reason: {activity.get('reason')}"
    )


def _add_text(parent: Element, name: str, value: object) -> None:
    node = SubElement(parent, name)
    node.text = "" if value is None else str(value)


def _xml_name(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))
