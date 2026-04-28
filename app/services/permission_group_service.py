from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.permission_group import PermissionGroup
from app.schemas.permission_group import PermissionGroupCreate, PermissionGroupUpdate


DEFAULT_USER_GROUP_TITLE = "User"
DEFAULT_ADMIN_GROUP_TITLE = "Admin"


def get_permission_group_by_title(db: Session, title: str):
    return db.query(PermissionGroup).filter(PermissionGroup.title == title).first()


def get_or_create_default_user_group(db: Session):
    group = get_permission_group_by_title(db, DEFAULT_USER_GROUP_TITLE)
    if group:
        return group

    group = PermissionGroup(
        title=DEFAULT_USER_GROUP_TITLE,
        description="Default user permission group",
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def get_or_create_admin_group(db: Session):
    group = get_permission_group_by_title(db, DEFAULT_ADMIN_GROUP_TITLE)
    if group:
        return group

    group = PermissionGroup(
        title=DEFAULT_ADMIN_GROUP_TITLE,
        description="Administrative permission group",
        is_admin=True,
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def list_permission_groups(db: Session):
    return db.query(PermissionGroup).order_by(PermissionGroup.title).all()


def get_permission_group(db: Session, permission_group_id: str):
    group = db.query(PermissionGroup).filter(PermissionGroup.id == permission_group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo de permissões não encontrado")

    return group


def create_permission_group(db: Session, data: PermissionGroupCreate):
    existing_group = get_permission_group_by_title(db, data.title)
    if existing_group:
        raise HTTPException(status_code=400, detail="Grupo de permissões já existe")

    group = PermissionGroup(**data.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def update_permission_group(db: Session, permission_group_id: str, data: PermissionGroupUpdate):
    group = get_permission_group(db, permission_group_id)

    update_data = data.model_dump(exclude_unset=True)
    if "title" in update_data:
        existing_group = get_permission_group_by_title(db, update_data["title"])
        if existing_group and existing_group.id != group.id:
            raise HTTPException(status_code=400, detail="Grupo de permissões já existe")

    for field, value in update_data.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)

    return group


def delete_permission_group(db: Session, permission_group_id: str):
    group = get_permission_group(db, permission_group_id)
    if group.users:
        raise HTTPException(
            status_code=400,
            detail="Grupo de permissões possui usuários vinculados",
        )

    db.delete(group)
    db.commit()
