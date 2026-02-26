"""initial alerts + invoices schema

Revision ID: ec247f9a356a
Revises: 
Create Date: 2026-02-25 23:06:48.347804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ec247f9a356a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Initial baseline – no-op
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Baseline downgrade – no-op
    pass
