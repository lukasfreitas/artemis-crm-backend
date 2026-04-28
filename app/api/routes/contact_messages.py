from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.contact_message import ContactMessageStatus
from app.schemas.contact_message import (
    ContactMessageCreate,
    ContactMessagePublicResponse,
    ContactMessageResponse,
    ContactMessageStatusUpdate,
)
from app.services.contact_message_service import (
    create_contact_message,
    get_contact_message,
    list_contact_messages,
    transition_contact_message_status,
)

router = APIRouter(prefix="/contact-messages", tags=["contact-messages"])


@router.post("", response_model=ContactMessagePublicResponse)
def create_message(data: ContactMessageCreate, db: Session = Depends(get_db)):
    return create_contact_message(db, data)


@router.get(
    "",
    response_model=list[ContactMessageResponse],
    dependencies=[Depends(require_admin)],
)
def list_messages(
    status: ContactMessageStatus | None = None,
    db: Session = Depends(get_db),
):
    return list_contact_messages(db, status)


@router.get(
    "/{contact_message_id}",
    response_model=ContactMessageResponse,
    dependencies=[Depends(require_admin)],
)
def get_message(contact_message_id: str, db: Session = Depends(get_db)):
    return get_contact_message(db, contact_message_id)


@router.patch(
    "/{contact_message_id}/status",
    response_model=ContactMessageResponse,
    dependencies=[Depends(require_admin)],
)
def update_message_status(
    contact_message_id: str,
    data: ContactMessageStatusUpdate,
    db: Session = Depends(get_db),
):
    return transition_contact_message_status(db, contact_message_id, data.status)
