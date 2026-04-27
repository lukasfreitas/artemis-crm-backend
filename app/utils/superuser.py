from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.services.auth_service import validate_password_strength


class SuperuserAlreadyExistsError(Exception):
    pass


def create_superuser(db: Session, email: str, password: str) -> User:
    validate_password_strength(password)

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise SuperuserAlreadyExistsError

    user = User(
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
