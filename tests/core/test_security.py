from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)

def test_hash_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_verify_password_correct():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_verify_password_incorrect():
    password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)
    assert not verify_password(wrong_password, hashed)


def test_create_access_token_contains_type():
    token = create_access_token({"sub": "user-id", "type": "access", "sid": "session-id"})
    payload = decode_token(token)

    assert payload["sub"] == "user-id"
    assert payload["type"] == "access"
    assert payload["sid"] == "session-id"


def test_create_refresh_token_contains_type():
    token = create_refresh_token({"sub": "user-id", "type": "refresh", "sid": "session-id"})
    payload = decode_token(token)

    assert payload["type"] == "refresh"


def test_hash_token_is_deterministic():
    token = "sample-token"
    assert hash_token(token) == hash_token(token)
