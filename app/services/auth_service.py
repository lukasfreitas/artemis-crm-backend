from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.auth_session import AuthSession
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.permission_group_service import get_or_create_default_user_group
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)


MIN_PASSWORD_LENGTH = 8


def utcnow():
    return datetime.now(timezone.utc)


def as_utc(value: datetime):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def validate_password_strength(password: str):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres",
        )


def register_user(db: Session, email: str, password: str):
    validate_password_strength(password)
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    permission_group = get_or_create_default_user_group(db)
    user = User(
        email=email,
        password_hash=hash_password(password),
        permission_group_id=permission_group.id,
    )
    user.profile = UserProfile()

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    return user


def build_token_response(db: Session, user: User):
    session = AuthSession(user_id=user.id, token_hash="", expires_at=utcnow())
    db.add(session)
    db.flush()

    access_token = create_access_token(
        {"sub": user.id, "type": "access", "sid": session.id}
    )
    refresh_token = create_refresh_token(
        {"sub": user.id, "type": "refresh", "sid": session.id}
    )

    refresh_payload = decode_token(refresh_token)
    session.token_hash = hash_token(refresh_token)
    session.expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)

    db.commit()
    db.refresh(session)
    db.refresh(user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user,
    }


def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    return build_token_response(db, user)


def refresh_user_session(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")

    session_id = payload.get("sid")
    user_id = payload.get("sub")

    session = db.query(AuthSession).filter(AuthSession.id == session_id).first()

    if not session or session.user_id != user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    if session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Sessão revogada")

    if as_utc(session.expires_at) <= utcnow():
        raise HTTPException(status_code=401, detail="Sessão expirada")

    if session.token_hash != hash_token(refresh_token):
        raise HTTPException(status_code=401, detail="Sessão inválida")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo")

    new_access_token = create_access_token(
        {"sub": user.id, "type": "access", "sid": session.id}
    )
    new_refresh_token = create_refresh_token(
        {"sub": user.id, "type": "refresh", "sid": session.id}
    )
    refresh_payload = decode_token(new_refresh_token)

    session.token_hash = hash_token(new_refresh_token)
    session.expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
    db.commit()
    db.refresh(user)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "user": user,
    }


def logout_user_session(db: Session, refresh_token: str):
    payload = decode_token(refresh_token, verify_exp=False)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")

    session_id = payload.get("sid")
    user_id = payload.get("sub")
    session = db.query(AuthSession).filter(AuthSession.id == session_id).first()

    if not session or session.user_id != user_id:
        raise HTTPException(status_code=401, detail="Sessão inválida")

    if session.token_hash != hash_token(refresh_token):
        raise HTTPException(status_code=401, detail="Sessão inválida")

    if session.revoked_at is None:
        session.revoked_at = utcnow()
        db.commit()
