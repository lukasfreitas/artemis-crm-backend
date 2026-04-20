from pydantic import BaseModel, ConfigDict, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(UserResponse):
    pass


# 🔐 LOGIN

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"