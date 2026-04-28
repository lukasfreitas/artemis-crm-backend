import pytest
from fastapi import HTTPException
from app.services.auth_service import (
    authenticate_user,
    login_user,
    logout_user_session,
    refresh_user_session,
    register_user,
)
from app.core.security import decode_token, hash_password
from app.models.auth_session import AuthSession
from app.models.user import User


def test_register_user_success(db_session):
    user = register_user(db_session, "user@example.com", "password123")

    assert user.email == "user@example.com"
    assert user.password_hash != "password123"
    assert user.is_active is True
    assert user.permission_group is not None
    assert user.permission_group.title == "User"
    assert user.is_admin is False


def test_register_user_duplicate(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        register_user(db_session, "user@example.com", "password123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email já cadastrado"


def test_authenticate_user_success(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    authenticated = authenticate_user(db_session, "user@example.com", "password123")

    assert authenticated.id == user.id
    assert authenticated.email == user.email


def test_authenticate_user_invalid_password(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(db_session, "user@example.com", "wrongpassword")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Credenciais inválidas"


def test_login_user_returns_token_pair(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    token_pair = login_user(db_session, "user@example.com", "password123")

    access_payload = decode_token(token_pair["access_token"])
    refresh_payload = decode_token(token_pair["refresh_token"])

    assert access_payload["sub"] == user.id
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == user.id
    assert refresh_payload["type"] == "refresh"
    assert token_pair["user"].id == user.id


def test_refresh_user_session_rotates_refresh_token(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    token_pair = login_user(db_session, "user@example.com", "password123")
    refreshed = refresh_user_session(db_session, token_pair["refresh_token"])

    assert refreshed["refresh_token"] != token_pair["refresh_token"]
    assert decode_token(refreshed["refresh_token"])["type"] == "refresh"


def test_refresh_user_session_rejects_revoked_session(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    token_pair = login_user(db_session, "user@example.com", "password123")
    logout_user_session(db_session, token_pair["refresh_token"])

    with pytest.raises(HTTPException) as exc_info:
        refresh_user_session(db_session, token_pair["refresh_token"])

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Sessão revogada"


def test_logout_user_session_revokes_session(db_session):
    user = User(email="user@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    token_pair = login_user(db_session, "user@example.com", "password123")
    payload = decode_token(token_pair["refresh_token"])

    logout_user_session(db_session, token_pair["refresh_token"])

    session = db_session.query(AuthSession).filter(AuthSession.id == payload["sid"]).first()

    assert session is not None
    assert session.revoked_at is not None
