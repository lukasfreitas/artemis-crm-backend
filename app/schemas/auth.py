from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(UserResponse):
    pass


# 🔐 LOGIN

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
