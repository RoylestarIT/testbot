"""user terms_accepted_at

Revision ID: c4a1f2b8e901
Revises: b2c4e8a91d03
Create Date: 2026-10-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4a1f2b8e901"
down_revision: Union[str, Sequence[str], None] = "b2c4e8a91d03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("terms_accepted_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE users SET terms_accepted_at = created_at WHERE terms_accepted_at IS NULL")


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("terms_accepted_at")
