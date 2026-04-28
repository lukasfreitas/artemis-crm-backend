"""create permission groups

Revision ID: 20260427_02
Revises: 20260427_01
Create Date: 2026-04-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_02"
down_revision = "20260427_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "permission_groups",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_influencer", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_index(
        op.f("ix_permission_groups_title"),
        "permission_groups",
        ["title"],
        unique=True,
    )

    op.execute(
        """
        INSERT INTO permission_groups (id, title, description, is_admin, is_influencer)
        VALUES
            ('default-admin-permission-group', 'Admin', 'Administrative permission group', true, false),
            ('default-user-permission-group', 'User', 'Default user permission group', false, false)
        """
    )

    op.add_column("users", sa.Column("permission_group_id", sa.String(), nullable=True))
    op.create_index(
        op.f("ix_users_permission_group_id"),
        "users",
        ["permission_group_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_users_permission_group_id_permission_groups",
        "users",
        "permission_groups",
        ["permission_group_id"],
        ["id"],
    )
    op.execute(
        """
        UPDATE users
        SET permission_group_id = CASE
            WHEN is_admin = true THEN 'default-admin-permission-group'
            ELSE 'default-user-permission-group'
        END
        """
    )
    op.drop_column("users", "is_admin")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute(
        """
        UPDATE users
        SET is_admin = permission_groups.is_admin
        FROM permission_groups
        WHERE users.permission_group_id = permission_groups.id
        """
    )
    op.drop_constraint(
        "fk_users_permission_group_id_permission_groups",
        "users",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_users_permission_group_id"), table_name="users")
    op.drop_column("users", "permission_group_id")
    op.drop_index(op.f("ix_permission_groups_title"), table_name="permission_groups")
    op.drop_table("permission_groups")
