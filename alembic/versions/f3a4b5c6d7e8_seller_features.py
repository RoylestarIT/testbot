"""seller features: digest, reply templates, sync error

Revision ID: f3a4b5c6d7e8
Revises: e1f2a3b4c5d6
Create Date: 2026-10-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("notify_daily_digest", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column("last_daily_digest_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("reply_templates", sa.JSON(), nullable=True))

    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("last_sync_error", sa.String(length=512), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.drop_column("last_sync_error")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("reply_templates")
        batch_op.drop_column("last_daily_digest_at")
        batch_op.drop_column("notify_daily_digest")
