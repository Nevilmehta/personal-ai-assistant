"""describe change

Revision ID: 460ce94a6f42
Revises: 4a4d2d25dcbc
Create Date: 2026-06-17 19:53:59.405498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '460ce94a6f42'
down_revision: Union[str, Sequence[str], None] = '4a4d2d25dcbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
