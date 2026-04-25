from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPairResponse,
    UserResponse,
)
from app.api.deps import get_current_active_user

from app.services.auth_service import (
    login_user,
    logout_user_session,
    refresh_user_session,
    register_user,
)

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password)
    return user

@router.post("/login", response_model=TokenPairResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token_pair = login_user(db, data.email, data.password)
    return TokenPairResponse(**token_pair)

@router.get("/me", response_model=UserResponse)
def me(user = Depends(get_current_active_user)):
    return user


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    token_pair = refresh_user_session(db, data.refresh_token)
    return TokenPairResponse(**token_pair)


@router.post("/logout", status_code=204)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    logout_user_session(db, data.refresh_token)
    return Response(status_code=204)
