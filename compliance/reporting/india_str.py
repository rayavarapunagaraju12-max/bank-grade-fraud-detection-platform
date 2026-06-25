from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4


def build_universal_case(case: dict) -> dict:
    transactions = case.get("transactions") or []
    total_amount = sum((Decimal(str(txn.get("amount", 0))) for txn in transactions), Decimal("0"))
    return {
        "case_id": case.get("case_id") or f"case_{uuid4().hex[:12]}",
        "created_at": datetime.now(UTC).isoformat(),
        "subject": {
            "account_id": case.get("account_id") or case.get("subject_account"),
            "customer_name": case.get("customer_name", "Unknown customer"),
            "customer_type": case.get("customer_type", "individual"),
            "country": case.get("country", "IN"),
            "pan": case.get("pan"),
            "beneficiary_id": case.get("beneficiary_id"),
        },
        "risk": {
            "score": case.get("risk_score"),
            "band": case.get("risk_band", "high"),
            "reason": case.get("reason", "Suspicious activity indicators exceeded review threshold."),
            "rules_triggered": case.get("rules_triggered", []),
            "sanctions_screening": case.get("sanctions_screening", {}),
        },
        "transactions": transactions,
        "total_amount": str(total_amount),
        "narrative": case.get("narrative"),
        "prepared_by": case.get("prepared_by", "system"),
    }


def generate_india_str(case: dict) -> dict:
    universal = build_universal_case(case)
    subject = universal["subject"]
    report_id = f"IN-STR-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
    return {
        "report_id": report_id,
        "report_type": "STR",
        "jurisdiction": "IN",
        "status": "draft_pending_compliance_review",
        "created_at": universal["created_at"],
        "reporting_entity": {
            "name": case.get("institution_name", "Demo Reporting Entity"),
            "registration_id": case.get("reporting_entity_id", "DEMO-RE-001"),
        },
        "principal_subject": subject,
        "suspicion_summary": {
            "total_amount": universal["total_amount"],
            "risk_score": universal["risk"]["score"],
            "risk_band": universal["risk"]["band"],
            "primary_reason": universal["risk"]["reason"],
            "rules_triggered": universal["risk"]["rules_triggered"],
            "sanctions_screening": universal["risk"]["sanctions_screening"],
        },
        "transactions": universal["transactions"],
        "narrative": universal["narrative"] or _narrative(universal),
        "review": {
            "prepared_by": universal["prepared_by"],
            "requires_human_approval": True,
            "target_regulator": "FIU-IND-style internal STR pack",
            "filing_mode": "draft_export_not_direct_filing",
        },
    }


def validate_india_str(report: dict) -> dict:
    errors = []
    warnings = []
    required_paths = [
        ("report_id",),
        ("report_type",),
        ("jurisdiction",),
        ("reporting_entity", "name"),
        ("principal_subject", "account_id"),
        ("principal_subject", "customer_name"),
        ("suspicion_summary", "primary_reason"),
        ("transactions",),
        ("narrative",),
    ]
    for path in required_paths:
        if not _get(report, path):
            errors.append({"path": ".".join(path), "message": "required field is missing"})

    if report.get("jurisdiction") != "IN":
        errors.append({"path": "jurisdiction", "message": "India STR report must use jurisdiction IN"})
    if report.get("report_type") != "STR":
        errors.append({"path": "report_type", "message": "India report type must be STR"})
    if not report.get("transactions"):
        errors.append({"path": "transactions", "message": "at least one suspicious transaction is required"})
    if not _get(report, ("principal_subject", "pan")):
        warnings.append({"path": "principal_subject.pan", "message": "PAN is recommended for Indian KYC evidence"})

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "schema": "FIU_IND_STYLE_INTERNAL_V1",
    }


def _narrative(case: dict) -> str:
    subject = case["subject"]
    risk = case["risk"]
    return (
        f"Account {subject.get('account_id')} for {subject.get('customer_name')} was flagged for STR review. "
        f"Total suspicious activity amount is {case.get('total_amount')}. "
        f"Primary reason: {risk.get('reason')}"
    )


def _get(payload: dict, path: tuple[str, ...]) -> object:
    current: object = payload
    for part in path:
        if not isinstance(current, dict) or not current.get(part):
            return None
        current = current[part]
    return current
