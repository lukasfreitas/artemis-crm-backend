"""Adicionando suporte para controle de sessões

Revision ID: c6c56dfb13ea
Revises: 20260425_02
Create Date: 2026-04-27 20:12:24.278591
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'c6c56dfb13ea'
down_revision = '20260425_02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("auth_sessions"):
        op.create_table(
            "auth_sessions",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("token_hash", sa.String(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = {index["name"] for index in inspector.get_indexes("auth_sessions")}
    if op.f("ix_auth_sessions_user_id") not in indexes:
        op.create_index(
            op.f("ix_auth_sessions_user_id"),
            "auth_sessions",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("auth_sessions"):
        indexes = {index["name"] for index in inspector.get_indexes("auth_sessions")}
        if op.f("ix_auth_sessions_user_id") in indexes:
            op.drop_index(op.f("ix_auth_sessions_user_id"), table_name="auth_sessions")
        op.drop_table("auth_sessions")
