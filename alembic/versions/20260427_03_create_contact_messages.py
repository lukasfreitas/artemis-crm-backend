"""create contact messages

Revision ID: 20260427_03
Revises: 20260427_02
Create Date: 2026-04-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_03"
down_revision = "20260427_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contact_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("whatsapp", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_contact_messages_email"),
        "contact_messages",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_contact_messages_status"),
        "contact_messages",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_contact_messages_status"), table_name="contact_messages")
    op.drop_index(op.f("ix_contact_messages_email"), table_name="contact_messages")
    op.drop_table("contact_messages")
