"""baseline existing training schema

Revision ID: 11cc733c5d98
Revises: 
Create Date: 2026-10-25 09:07:42.855040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11cc733c5d98'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the original training table."""
    op.create_table(
        "training",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=True),
        sa.Column("date", sa.Text(), nullable=False),
        sa.Column("shots", sa.Integer(), nullable=False),
        sa.Column("made", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    """Remove the original training table."""
    op.drop_table("training")
