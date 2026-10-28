"""add users and training ownership

Revision ID: 3fbc45d5e8ec
Revises: 11cc733c5d98
Create Date: 2026-10-27 18:47:30.610315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fbc45d5e8ec'
down_revision: Union[str, Sequence[str], None] = '11cc733c5d98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add users and training ownership."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    op.add_column(
        "training",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    connection = op.get_bind()

    connection.execute(
        sa.text("INSERT INTO users (username) VALUES (:username)"),
        {"username": "Richard"},
    )

    user_id = connection.execute(
        sa.text("SELECT id FROM users WHERE username = :username"),
        {"username": "Richard"},
    ).scalar_one()

    connection.execute(
        sa.text(
            "UPDATE training SET user_id = :user_id "
            "WHERE user_id IS NULL"
        ),
        {"user_id": user_id},
    )

    with op.batch_alter_table("training") as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_training_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )

    


def downgrade() -> None:
    """Remove training ownership and the users table."""
    with op.batch_alter_table("training") as batch_op:
        batch_op.drop_constraint(
            "fk_training_user_id_users",
            type_="foreignkey",
        )
        batch_op.drop_column("user_id")

    op.drop_table("users")