"""add due_date to invoices

Revision ID: 4144765e814c
Revises: ec247f9a356a
Create Date: 2026-02-25 23:09:28.374149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4144765e814c"
down_revision: Union[str, Sequence[str], None] = "ec247f9a356a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "invoices",
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("invoices", "due_date")
