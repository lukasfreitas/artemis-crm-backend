from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# 🔑 HASH

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# 🔐 JWT

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    issued_at = datetime.now(timezone.utc)
    expire = issued_at + expires_delta

    to_encode.update({
        "exp": expire,
        "iat": issued_at,
        "jti": str(uuid4()),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta = None):
    return create_token(
        data,
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    return create_token(
        data,
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, verify_exp: bool = True):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": verify_exp},
        )
        return payload
    except JWTError:
        return None


def hash_token(token: str):
    return sha256(token.encode("utf-8")).hexdigest()
