"""dashboard trial snooze fields

Revision ID: d7e8f9a0b1c2
Revises: c4a1f2b8e901
Create Date: 2026-10-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, Sequence[str], None] = "c4a1f2b8e901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("onboarding_completed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("trial_pro_until", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(
            sa.Column("trial_pro_used", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column("free_api_publishes_remaining", sa.Integer(), nullable=False, server_default="3")
        )

    with op.batch_alter_table("reviews", schema=None) as batch_op:
        batch_op.add_column(sa.Column("snoozed_until", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("reviews", schema=None) as batch_op:
        batch_op.drop_column("snoozed_until")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("free_api_publishes_remaining")
        batch_op.drop_column("trial_pro_used")
        batch_op.drop_column("trial_pro_until")
        batch_op.drop_column("onboarding_completed_at")
