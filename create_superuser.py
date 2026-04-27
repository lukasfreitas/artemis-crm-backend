import argparse
import getpass
import json
import sys

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.database import SessionLocal
from app.models import user  # noqa: F401
from app.utils.superuser import SuperuserAlreadyExistsError, create_superuser


def log_event(level: str, event: str, **fields):
    payload = {"level": level, "event": event, **fields}
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cria um usuario administrador."
    )
    parser.add_argument("--email", required=True, help="Email do superusuario")
    parser.add_argument(
        "--password",
        help="Senha do superusuario. Se omitida, sera solicitada interativamente.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    password = args.password or getpass.getpass("Password: ")

    db = SessionLocal()
    try:
        admin_user = create_superuser(db, args.email, password)
        log_event(
            "info",
            "superuser_created",
            user_id=admin_user.id,
            email=admin_user.email,
            is_admin=admin_user.is_admin,
        )
        return 0
    except SuperuserAlreadyExistsError:
        db.rollback()
        log_event(
            "error",
            "superuser_create_failed",
            reason="user_already_exists",
            email=args.email,
        )
        return 1
    except HTTPException as exc:
        db.rollback()
        log_event(
            "error",
            "superuser_create_failed",
            reason="validation_error",
            detail=exc.detail,
            status_code=exc.status_code,
            email=args.email,
        )
        return 1
    except IntegrityError as exc:
        db.rollback()
        log_event(
            "error",
            "superuser_create_failed",
            reason="integrity_error",
            detail=str(exc.orig),
            email=args.email,
        )
        return 1
    except SQLAlchemyError as exc:
        db.rollback()
        log_event(
            "error",
            "superuser_create_failed",
            reason="database_error",
            detail=str(exc),
            email=args.email,
        )
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
