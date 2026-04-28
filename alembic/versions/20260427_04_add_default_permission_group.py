"""add default permission group

Revision ID: 20260427_04
Revises: 20260427_03
Create Date: 2026-04-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_04"
down_revision = "20260427_03"
branch_labels = None
depends_on = None


ADMIN_GROUP_ID = "11111111-1111-4111-8111-111111111111"
USER_GROUP_ID = "22222222-2222-4222-8222-222222222222"
OLD_ADMIN_GROUP_ID = "default-admin-permission-group"
OLD_USER_GROUP_ID = "default-user-permission-group"


def upgrade() -> None:
    op.add_column(
        "permission_groups",
        sa.Column(
            "is_default_type",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.drop_constraint(
        "fk_users_permission_group_id_permission_groups",
        "users",
        type_="foreignkey",
    )
    op.execute(
        f"""
        UPDATE permission_groups
        SET id = '{ADMIN_GROUP_ID}'
        WHERE id = '{OLD_ADMIN_GROUP_ID}'
        """
    )
    op.execute(
        f"""
        UPDATE permission_groups
        SET id = '{USER_GROUP_ID}', is_default_type = true
        WHERE id = '{OLD_USER_GROUP_ID}'
        """
    )
    op.execute(
        f"""
        UPDATE users
        SET permission_group_id = CASE
            WHEN permission_group_id = '{OLD_ADMIN_GROUP_ID}' THEN '{ADMIN_GROUP_ID}'
            WHEN permission_group_id = '{OLD_USER_GROUP_ID}' THEN '{USER_GROUP_ID}'
            ELSE permission_group_id
        END
        """
    )
    op.create_foreign_key(
        "fk_users_permission_group_id_permission_groups",
        "users",
        "permission_groups",
        ["permission_group_id"],
        ["id"],
    )
    op.create_index(
        "uq_permission_groups_default_type",
        "permission_groups",
        ["is_default_type"],
        unique=True,
        postgresql_where=sa.text("is_default_type = true"),
    )
    op.alter_column("permission_groups", "is_default_type", server_default=None)


def downgrade() -> None:
    op.drop_index("uq_permission_groups_default_type", table_name="permission_groups")
    op.drop_constraint(
        "fk_users_permission_group_id_permission_groups",
        "users",
        type_="foreignkey",
    )
    op.execute(
        f"""
        UPDATE permission_groups
        SET id = '{OLD_ADMIN_GROUP_ID}'
        WHERE id = '{ADMIN_GROUP_ID}'
        """
    )
    op.execute(
        f"""
        UPDATE permission_groups
        SET id = '{OLD_USER_GROUP_ID}'
        WHERE id = '{USER_GROUP_ID}'
        """
    )
    op.execute(
        f"""
        UPDATE users
        SET permission_group_id = CASE
            WHEN permission_group_id = '{ADMIN_GROUP_ID}' THEN '{OLD_ADMIN_GROUP_ID}'
            WHEN permission_group_id = '{USER_GROUP_ID}' THEN '{OLD_USER_GROUP_ID}'
            ELSE permission_group_id
        END
        """
    )
    op.create_foreign_key(
        "fk_users_permission_group_id_permission_groups",
        "users",
        "permission_groups",
        ["permission_group_id"],
        ["id"],
    )
    op.drop_column("permission_groups", "is_default_type")
