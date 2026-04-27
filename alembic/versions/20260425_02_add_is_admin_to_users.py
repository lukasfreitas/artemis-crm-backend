"""add is_admin to users

Revision ID: 20260425_02
Revises: 20260425_01
Create Date: 2026-04-25 00:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260425_02"
down_revision = "20260425_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "is_admin", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_admin")
