"""unique telegram payment charge id per subscription

Revision ID: i7d8e9f0a1b2
Revises: h6c7d8e9f0a1
Create Date: 2026-10-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "i7d8e9f0a1b2"
down_revision: Union[str, None] = "h6c7d8e9f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_WHERE = sa.text("payment_method IN ('stars', 'telegram')")


def upgrade() -> None:
    op.create_index(
        "uq_subscription_telegram_charge",
        "subscriptions",
        ["external_payment_id"],
        unique=True,
        sqlite_where=_WHERE,
        postgresql_where=_WHERE,
    )


def downgrade() -> None:
    op.drop_index("uq_subscription_telegram_charge", table_name="subscriptions")
