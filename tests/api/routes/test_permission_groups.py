from faker import Faker

from app.core.security import hash_password
from app.models.permission_group import PermissionGroup
from app.models.user import User

faker = Faker()


def authenticate(client, db_session, permission_group):
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


def test_create_permission_group_requires_admin(client, db_session):
    group = PermissionGroup(title="Member")
    db_session.add(group)
    db_session.commit()

    token = authenticate(client, db_session, group)

    response = client.post(
        "/permission-groups",
        json={"title": "Influencer", "is_influencer": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acesso negado"


def test_create_permission_group_as_admin(client, db_session):
    admin_group = PermissionGroup(title="Admin", is_admin=True)
    db_session.add(admin_group)
    db_session.commit()

    token = authenticate(client, db_session, admin_group)

    response = client.post(
        "/permission-groups",
        json={
            "title": "Influencer",
            "description": "Influencer users",
            "is_influencer": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Influencer"
    assert data["description"] == "Influencer users"
    assert data["is_admin"] is False
    assert data["is_influencer"] is True
    assert data["is_default_type"] is False


def test_create_default_permission_group_as_admin_unsets_previous_default(client, db_session):
    admin_group = PermissionGroup(title="Admin", is_admin=True)
    previous_default = PermissionGroup(title="Member", is_default_type=True)
    db_session.add_all([admin_group, previous_default])
    db_session.commit()

    token = authenticate(client, db_session, admin_group)

    response = client.post(
        "/permission-groups",
        json={"title": "Influencer", "is_default_type": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    db_session.refresh(previous_default)

    assert response.status_code == 200
    assert response.json()["is_default_type"] is True
    assert previous_default.is_default_type is False


def test_list_permission_groups_as_admin(client, db_session):
    admin_group = PermissionGroup(title="Admin", is_admin=True)
    member_group = PermissionGroup(title="Member")
    db_session.add_all([admin_group, member_group])
    db_session.commit()

    token = authenticate(client, db_session, admin_group)

    response = client.get(
        "/permission-groups",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert [group["title"] for group in response.json()] == ["Admin", "Member"]


def test_auth_me_returns_permission_group(client, db_session):
    group = PermissionGroup(title="Influencer", is_influencer=True)
    db_session.add(group)
    db_session.commit()

    token = authenticate(client, db_session, group)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_admin"] is False
    assert data["is_influencer"] is True
    assert data["permission_group"]["title"] == "Influencer"
