from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.schemas.permission_group import (
    PermissionGroupCreate,
    PermissionGroupResponse,
    PermissionGroupUpdate,
)
from app.services.permission_group_service import (
    create_permission_group,
    delete_permission_group,
    get_permission_group,
    list_permission_groups,
    update_permission_group,
)

router = APIRouter(
    prefix="/permission-groups",
    tags=["permission-groups"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[PermissionGroupResponse])
def list_groups(db: Session = Depends(get_db)):
    return list_permission_groups(db)


@router.post("", response_model=PermissionGroupResponse)
def create_group(data: PermissionGroupCreate, db: Session = Depends(get_db)):
    return create_permission_group(db, data)


@router.get("/{permission_group_id}", response_model=PermissionGroupResponse)
def get_group(permission_group_id: str, db: Session = Depends(get_db)):
    return get_permission_group(db, permission_group_id)


@router.patch("/{permission_group_id}", response_model=PermissionGroupResponse)
def update_group(
    permission_group_id: str,
    data: PermissionGroupUpdate,
    db: Session = Depends(get_db),
):
    return update_permission_group(db, permission_group_id, data)


@router.delete("/{permission_group_id}", status_code=204)
def delete_group(permission_group_id: str, db: Session = Depends(get_db)):
    delete_permission_group(db, permission_group_id)
    return Response(status_code=204)
