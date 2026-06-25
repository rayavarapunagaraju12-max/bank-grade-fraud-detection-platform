"""Initial fraud platform schema.

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260614_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("transaction_id"),
    )
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])

    op.create_table(
        "alerts",
        sa.Column("alert_id", sa.String(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("risk_band", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("alert_id"),
    )
    op.create_index("ix_alerts_transaction_id", "alerts", ["transaction_id"])
    op.create_index("ix_alerts_score", "alerts", ["score"])
    op.create_index("ix_alerts_risk_band", "alerts", ["risk_band"])
    op.create_index("ix_alerts_status", "alerts", ["status"])

    op.create_table(
        "audit_logs",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_audit_logs_actor", "audit_logs", ["actor"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])

    op.create_table(
        "watchlist_entries",
        sa.Column("entry_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("list_name", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("normalized_name", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("identifiers", sa.JSON(), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("entry_id"),
    )
    op.create_index("ix_watchlist_entries_source", "watchlist_entries", ["source"])
    op.create_index("ix_watchlist_entries_list_name", "watchlist_entries", ["list_name"])
    op.create_index("ix_watchlist_entries_entity_type", "watchlist_entries", ["entity_type"])
    op.create_index("ix_watchlist_entries_name", "watchlist_entries", ["name"])
    op.create_index("ix_watchlist_entries_normalized_name", "watchlist_entries", ["normalized_name"])
    op.create_index("ix_watchlist_entries_country", "watchlist_entries", ["country"])

    op.create_table(
        "watchlist_ingestions",
        sa.Column("ingestion_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("records_seen", sa.Integer(), nullable=False),
        sa.Column("records_loaded", sa.Integer(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("metadata_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("ingestion_id"),
    )
    op.create_index("ix_watchlist_ingestions_source", "watchlist_ingestions", ["source"])
    op.create_index("ix_watchlist_ingestions_status", "watchlist_ingestions", ["status"])

    op.create_table(
        "compliance_reports",
        sa.Column("report_id", sa.String(), nullable=False),
        sa.Column("report_type", sa.String(), nullable=False),
        sa.Column("jurisdiction", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("subject_account", sa.String(), nullable=True),
        sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("report_id"),
    )
    op.create_index("ix_compliance_reports_report_type", "compliance_reports", ["report_type"])
    op.create_index("ix_compliance_reports_jurisdiction", "compliance_reports", ["jurisdiction"])
    op.create_index("ix_compliance_reports_status", "compliance_reports", ["status"])
    op.create_index("ix_compliance_reports_subject_account", "compliance_reports", ["subject_account"])


def downgrade() -> None:
    op.drop_table("compliance_reports")
    op.drop_table("watchlist_ingestions")
    op.drop_table("watchlist_entries")
    op.drop_table("audit_logs")
    op.drop_table("alerts")
    op.drop_table("transactions")
