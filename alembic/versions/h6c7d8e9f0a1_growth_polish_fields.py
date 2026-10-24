"""growth: start sources, nudges, ozon questions cache

Revision ID: h6c7d8e9f0a1
Revises: g5b6c7d8e9f0
Create Date: 2026-10-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h6c7d8e9f0a1"
down_revision: Union[str, None] = "g5b6c7d8e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("start_source_counts", sa.JSON(), nullable=True))
        batch_op.add_column(
            sa.Column("onboarding_stuck_nudge_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("trial_ended_notice_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("trial_ended_ack_at", sa.DateTime(timezone=True), nullable=True)
        )
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("cached_unanswered_ozon_questions", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.drop_column("cached_unanswered_ozon_questions")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("trial_ended_ack_at")
        batch_op.drop_column("trial_ended_notice_at")
        batch_op.drop_column("onboarding_stuck_nudge_at")
        batch_op.drop_column("start_source_counts")
