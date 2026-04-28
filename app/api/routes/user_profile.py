from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user_profile import UserProfileResponse, UserProfileUpdate
from app.services.user_profile_service import (
    get_or_create_user_profile,
    update_user_profile,
)

router = APIRouter(prefix="/users/me/profile", tags=["user-profile"])


@router.get("", response_model=UserProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return get_or_create_user_profile(db, user)


@router.patch("", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return update_user_profile(db, user, data)
