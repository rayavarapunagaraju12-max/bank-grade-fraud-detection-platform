"""Add bank-grade investigation workflow fields.

Revision ID: 20260623_0002
Revises: 20260614_0001
Create Date: 2026-06-23
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260623_0002"
down_revision: str | None = "20260614_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("assigned_to", sa.String(), nullable=True))
    op.add_column("alerts", sa.Column("decision", sa.String(), nullable=True))
    op.add_column("alerts", sa.Column("decision_notes", sa.String(), nullable=True))
    op.add_column("alerts", sa.Column("reviewed_by", sa.String(), nullable=True))
    op.add_column("alerts", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "alerts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index("ix_alerts_assigned_to", "alerts", ["assigned_to"])
    op.create_index("ix_alerts_decision", "alerts", ["decision"])
    op.create_index("ix_alerts_reviewed_by", "alerts", ["reviewed_by"])


def downgrade() -> None:
    op.drop_index("ix_alerts_reviewed_by", table_name="alerts")
    op.drop_index("ix_alerts_decision", table_name="alerts")
    op.drop_index("ix_alerts_assigned_to", table_name="alerts")
    op.drop_column("alerts", "updated_at")
    op.drop_column("alerts", "resolved_at")
    op.drop_column("alerts", "reviewed_by")
    op.drop_column("alerts", "decision_notes")
    op.drop_column("alerts", "decision")
    op.drop_column("alerts", "assigned_to")
