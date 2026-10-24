"""product news seen + calculator preset volume

Revision ID: e2f3a4b5c6d7
Revises: d4e5f6a7b8c9
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("product_news_seen_version", sa.String(length=32), nullable=False, server_default="")
        )
        batch_op.add_column(sa.Column("calc_preset_volume", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("calc_preset_volume")
        batch_op.drop_column("product_news_seen_version")
