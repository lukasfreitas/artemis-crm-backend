from faker import Faker

from app.core.security import hash_password
from app.models.contact_message import ContactMessage
from app.models.permission_group import PermissionGroup
from app.models.user import User

faker = Faker()


def contact_message_payload(email="lead@example.com"):
    return {
        "full_name": "Lead Name",
        "email": email,
        "whatsapp": "+5511999999999",
        "company": "Lead Company",
        "message": "Gostaria de saber mais sobre o sistema.",
    }


def authenticate(client, db_session, is_admin=False):
    permission_group = PermissionGroup(title=faker.word(), is_admin=is_admin)
    db_session.add(permission_group)
    db_session.commit()

    email = faker.email()
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        permission_group_id=permission_group.id,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )

    return response.json()["access_token"]


def test_create_contact_message_public(client):
    response = client.post(
        "/contact-messages",
        json=contact_message_payload(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["status"] == "new"


def test_create_contact_message_validates_payload(client):
    response = client.post(
        "/contact-messages",
        json={
            "full_name": "A",
            "email": "invalid-email",
            "whatsapp": "123",
            "message": "Oi",
        },
    )

    assert response.status_code == 422


def test_list_contact_messages_requires_admin(client, db_session):
    token = authenticate(client, db_session, is_admin=False)

    response = client.get(
        "/contact-messages",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso negado"


def test_list_contact_messages_as_admin(client, db_session):
    token = authenticate(client, db_session, is_admin=True)
    contact_message = ContactMessage(**contact_message_payload("lead@example.com"))
    db_session.add(contact_message)
    db_session.commit()

    response = client.get(
        "/contact-messages",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "lead@example.com"
    assert data[0]["status"] == "new"


def test_update_contact_message_status_as_admin(client, db_session):
    token = authenticate(client, db_session, is_admin=True)
    contact_message = ContactMessage(**contact_message_payload("lead@example.com"))
    db_session.add(contact_message)
    db_session.commit()
    db_session.refresh(contact_message)

    response = client.patch(
        f"/contact-messages/{contact_message.id}/status",
        json={"status": "in_progress"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_update_contact_message_status_rejects_invalid_transition(client, db_session):
    token = authenticate(client, db_session, is_admin=True)
    contact_message = ContactMessage(**contact_message_payload("lead@example.com"))
    db_session.add(contact_message)
    db_session.commit()
    db_session.refresh(contact_message)

    response = client.patch(
        f"/contact-messages/{contact_message.id}/status",
        json={"status": "converted"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Transição de status inválida: new -> converted"
