"""add cache_creation_tokens to cost_log

Revision ID: a3d8e2f91b4c
Revises: 9f4bce7a1d2e
Create Date: 2026-05-25 21:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3d8e2f91b4c"
down_revision: Union[str, Sequence[str], None] = "9f4bce7a1d2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("cost_log") as batch_op:
        batch_op.add_column(
            sa.Column("cache_creation_tokens", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("cost_log") as batch_op:
        batch_op.drop_column("cache_creation_tokens")
