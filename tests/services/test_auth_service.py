import pytest
from fastapi import HTTPException
from app.services.auth_service import register_user, authenticate_user, generate_token
from app.core.security import hash_password, decode_token
from app.models.user import User


def test_register_user_success(db_session):
    user = register_user(db_session, "user@example.com", "password123")

    assert user.email == "user@example.com"
    assert user.password_hash != "password123"
    assert user.is_active is True


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

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Credenciais inválidas"


def test_generate_token_contains_user_id():
    user = User(id="test-id")
    token = generate_token(user)
    payload = decode_token(token)

    assert payload["sub"] == "test-id"
