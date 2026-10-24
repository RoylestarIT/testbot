"""user profile, feedback counters

Revision ID: f4a5b6c7d8e9
Revises: e2f3a4b5c6d7
Create Date: 2026-10-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f4a5b6c7d8e9"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "ui_timezone",
                sa.String(length=64),
                nullable=False,
                server_default="Europe/Minsk",
            )
        )
        batch_op.add_column(
            sa.Column(
                "ui_language",
                sa.String(length=8),
                nullable=False,
                server_default="ru",
            )
        )
        batch_op.add_column(
            sa.Column("publish_actions_count", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("reply_feedback_up", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("reply_feedback_down", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("reply_feedback_down")
        batch_op.drop_column("reply_feedback_up")
        batch_op.drop_column("publish_actions_count")
        batch_op.drop_column("ui_language")
        batch_op.drop_column("ui_timezone")
