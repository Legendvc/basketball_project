"""align training primary key nullability

Revision ID: e80d70b04c42
Revises: 3fbc45d5e8ec
Create Date: 2026-10-28 07:27:43.353043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e80d70b04c42'
down_revision: Union[str, Sequence[str], None] = '3fbc45d5e8ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align training.id with the ORM model."""
    with op.batch_alter_table("training") as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )


def downgrade() -> None:
    """Restore the previous training.id declaration."""
    with op.batch_alter_table("training") as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
        )
