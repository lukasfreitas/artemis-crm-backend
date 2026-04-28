from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.contact_message import ContactMessage, ContactMessageStatus
from app.schemas.contact_message import ContactMessageCreate


ALLOWED_STATUS_TRANSITIONS = {
    ContactMessageStatus.NEW: {
        ContactMessageStatus.IN_PROGRESS,
        ContactMessageStatus.CONTACTED,
        ContactMessageStatus.DISCARDED,
    },
    ContactMessageStatus.IN_PROGRESS: {
        ContactMessageStatus.CONTACTED,
        ContactMessageStatus.DISCARDED,
    },
    ContactMessageStatus.CONTACTED: {
        ContactMessageStatus.CONVERTED,
        ContactMessageStatus.DISCARDED,
    },
    ContactMessageStatus.CONVERTED: set(),
    ContactMessageStatus.DISCARDED: set(),
}


def create_contact_message(db: Session, data: ContactMessageCreate):
    contact_message = ContactMessage(**data.model_dump())
    db.add(contact_message)
    db.commit()
    db.refresh(contact_message)

    return contact_message


def list_contact_messages(db: Session, status: ContactMessageStatus | None = None):
    query = db.query(ContactMessage)
    if status is not None:
        query = query.filter(ContactMessage.status == status.value)

    return query.order_by(ContactMessage.created_at.desc()).all()


def get_contact_message(db: Session, contact_message_id: str):
    contact_message = (
        db.query(ContactMessage)
        .filter(ContactMessage.id == contact_message_id)
        .first()
    )
    if not contact_message:
        raise HTTPException(status_code=404, detail="Mensagem de contato não encontrada")

    return contact_message


def transition_contact_message_status(
    db: Session,
    contact_message_id: str,
    next_status: ContactMessageStatus,
):
    contact_message = get_contact_message(db, contact_message_id)
    current_status = ContactMessageStatus(contact_message.status)

    if current_status == next_status:
        return contact_message

    allowed_next_statuses = ALLOWED_STATUS_TRANSITIONS[current_status]
    if next_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Transição de status inválida: "
                f"{current_status.value} -> {next_status.value}"
            ),
        )

    contact_message.status = next_status.value
    db.commit()
    db.refresh(contact_message)

    return contact_message
