"""marketplace polish fields

Revision ID: b2c4e8a91d03
Revises: fa643290011e
Create Date: 2026-10-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c4e8a91d03"
down_revision: Union[str, Sequence[str], None] = "fa643290011e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("auto_publish_enabled", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("tone_profiles", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("tone_profiles", schema=None) as batch_op:
        batch_op.drop_column("is_default")

    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.drop_column("last_sync_at")
        batch_op.drop_column("auto_publish_enabled")
