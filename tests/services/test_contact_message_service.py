import pytest
from fastapi import HTTPException

from app.models.contact_message import ContactMessageStatus
from app.schemas.contact_message import ContactMessageCreate
from app.services.contact_message_service import (
    create_contact_message,
    list_contact_messages,
    transition_contact_message_status,
)


def make_contact_message_data(email="lead@example.com"):
    return ContactMessageCreate(
        full_name="Lead Name",
        email=email,
        whatsapp="+5511999999999",
        company="Lead Company",
        message="Gostaria de saber mais sobre o sistema.",
    )


def test_create_contact_message_starts_as_new(db_session):
    contact_message = create_contact_message(db_session, make_contact_message_data())

    assert contact_message.full_name == "Lead Name"
    assert contact_message.email == "lead@example.com"
    assert contact_message.status == ContactMessageStatus.NEW.value
    assert contact_message.created_at is not None
    assert contact_message.updated_at is not None


def test_list_contact_messages_can_filter_by_status(db_session):
    create_contact_message(db_session, make_contact_message_data("new@example.com"))
    contacted = create_contact_message(db_session, make_contact_message_data("contacted@example.com"))
    transition_contact_message_status(
        db_session,
        contacted.id,
        ContactMessageStatus.CONTACTED,
    )

    messages = list_contact_messages(db_session, ContactMessageStatus.CONTACTED)

    assert len(messages) == 1
    assert messages[0].email == "contacted@example.com"


def test_transition_contact_message_status_valid_flow(db_session):
    contact_message = create_contact_message(db_session, make_contact_message_data())

    in_progress = transition_contact_message_status(
        db_session,
        contact_message.id,
        ContactMessageStatus.IN_PROGRESS,
    )
    assert in_progress.status == ContactMessageStatus.IN_PROGRESS.value

    contacted = transition_contact_message_status(
        db_session,
        contact_message.id,
        ContactMessageStatus.CONTACTED,
    )
    assert contacted.status == ContactMessageStatus.CONTACTED.value

    converted = transition_contact_message_status(
        db_session,
        contact_message.id,
        ContactMessageStatus.CONVERTED,
    )
    assert converted.status == ContactMessageStatus.CONVERTED.value


def test_transition_contact_message_status_rejects_invalid_flow(db_session):
    contact_message = create_contact_message(db_session, make_contact_message_data())

    with pytest.raises(HTTPException) as exc_info:
        transition_contact_message_status(
            db_session,
            contact_message.id,
            ContactMessageStatus.CONVERTED,
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Transição de status inválida: new -> converted"
