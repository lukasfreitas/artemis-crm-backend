from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileUpdate


def get_or_create_user_profile(db: Session, user: User):
    if user.profile:
        return user.profile

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    db.refresh(user)

    return profile


def update_user_profile(db: Session, user: User, data: UserProfileUpdate):
    profile = get_or_create_user_profile(db, user)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    db.refresh(user)

    return profile
