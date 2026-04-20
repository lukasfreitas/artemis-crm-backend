from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user

from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_token
)

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = authenticate_user(db, data.email, data.password)
    token = generate_token(user)

    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def me(user = Depends(get_current_user)):
    return user