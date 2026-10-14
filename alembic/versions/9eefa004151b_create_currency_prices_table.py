"""create currency prices table

Revision ID: 9eefa004151b
Revises: 
Create Date: 2026-10-14 18:49:25.483178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9eefa004151b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "currency_prices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_currency_prices_ticker", "currency_prices", ["ticker"])


def downgrade() -> None:
    op.drop_index("ix_currency_prices_ticker", table_name="currency_prices")
    op.drop_table("currency_prices")
