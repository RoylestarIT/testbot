"""soft recommend + auto stop words

Revision ID: d4e5f6a7b8c9
Revises: c8d9e0f1a2b3
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "soft_product_recommend",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("auto_publish_stop_words", sa.String(512), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("marketplace_accounts", schema=None) as batch_op:
        batch_op.drop_column("auto_publish_stop_words")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("soft_product_recommend")
