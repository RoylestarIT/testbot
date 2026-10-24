"""P1: questions cache, auto rules, notify pref

Revision ID: c8d9e0f1a2b3
Revises: a9b8c7d6e5f4
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "notify_buyer_questions",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )

    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "auto_publish_min_rating",
                sa.Integer(),
                nullable=False,
                server_default="4",
            )
        )
        batch_op.add_column(
            sa.Column(
                "auto_publish_stars_only",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "cached_unanswered_questions",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.drop_column("cached_unanswered_questions")
        batch_op.drop_column("auto_publish_stars_only")
        batch_op.drop_column("auto_publish_min_rating")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("notify_buyer_questions")
