from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.services.auth_service import validate_password_strength
from app.services.permission_group_service import get_or_create_admin_group


class SuperuserAlreadyExistsError(Exception):
    pass


def create_superuser(db: Session, email: str, password: str) -> User:
    validate_password_strength(password)

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise SuperuserAlreadyExistsError

    permission_group = get_or_create_admin_group(db)
    user = User(
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        permission_group_id=permission_group.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
