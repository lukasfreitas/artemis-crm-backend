import pytest
from fastapi import HTTPException

from app.models.permission_group import PermissionGroup
from app.schemas.permission_group import PermissionGroupCreate, PermissionGroupUpdate
from app.services.permission_group_service import (
    create_permission_group,
    delete_permission_group,
    get_or_create_admin_group,
    get_or_create_default_user_group,
    update_permission_group,
)


def test_get_or_create_default_user_group(db_session):
    group = get_or_create_default_user_group(db_session)

    assert group.title == "User"
    assert group.is_admin is False
    assert group.is_influencer is False


def test_get_or_create_admin_group(db_session):
    group = get_or_create_admin_group(db_session)

    assert group.title == "Admin"
    assert group.is_admin is True
    assert group.is_influencer is False


def test_create_permission_group(db_session):
    group = create_permission_group(
        db_session,
        PermissionGroupCreate(
            title="Influencer",
            description="Influencer users",
            is_influencer=True,
        ),
    )

    assert group.title == "Influencer"
    assert group.description == "Influencer users"
    assert group.is_influencer is True


def test_create_permission_group_rejects_duplicate_title(db_session):
    db_session.add(PermissionGroup(title="Manager"))
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        create_permission_group(db_session, PermissionGroupCreate(title="Manager"))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Grupo de permissões já existe"


def test_update_permission_group(db_session):
    group = PermissionGroup(title="Member")
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    updated = update_permission_group(
        db_session,
        group.id,
        PermissionGroupUpdate(title="Editor", is_influencer=True),
    )

    assert updated.title == "Editor"
    assert updated.is_influencer is True


def test_delete_permission_group(db_session):
    group = PermissionGroup(title="Temporary")
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    delete_permission_group(db_session, group.id)

    assert db_session.query(PermissionGroup).filter(PermissionGroup.id == group.id).first() is None
