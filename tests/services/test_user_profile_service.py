from app.core.security import hash_password
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileUpdate
from app.services.user_profile_service import (
    get_or_create_user_profile,
    update_user_profile,
)


def test_get_or_create_user_profile_creates_profile(db_session):
    user = User(email="profile@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = get_or_create_user_profile(db_session, user)

    assert profile.user_id == user.id
    assert profile.cell_number is None
    assert profile.first_name is None
    assert profile.last_name is None


def test_get_or_create_user_profile_reuses_existing_profile(db_session):
    user = User(email="profile@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    existing_profile = UserProfile(user_id=user.id, first_name="Existing")
    db_session.add(existing_profile)
    db_session.commit()
    db_session.refresh(user)

    profile = get_or_create_user_profile(db_session, user)

    assert profile.id == existing_profile.id
    assert profile.first_name == "Existing"


def test_update_user_profile_updates_only_sent_fields(db_session):
    user = User(email="profile@example.com", password_hash=hash_password("password123"))
    user.profile = UserProfile(first_name="Old", last_name="Name")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = update_user_profile(
        db_session,
        user,
        UserProfileUpdate(first_name="New", cell_number="+5511888888888"),
    )

    assert profile.first_name == "New"
    assert profile.last_name == "Name"
    assert profile.cell_number == "+5511888888888"
