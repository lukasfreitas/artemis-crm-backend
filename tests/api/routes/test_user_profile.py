from faker import Faker

from app.core.security import hash_password
from app.models.user import User
from app.models.user_profile import UserProfile

faker = Faker()


def authenticate(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )

    return response.json()["access_token"], user


def test_get_profile_creates_empty_profile(client, db_session):
    token, user = authenticate(client, db_session)

    response = client.get(
        "/users/me/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["cell_number"] is None
    assert data["first_name"] is None
    assert data["last_name"] is None

    db_session.refresh(user)
    assert user.profile is not None


def test_update_profile(client, db_session):
    token, user = authenticate(client, db_session)

    response = client.patch(
        "/users/me/profile",
        json={
            "cell_number": "+5511999999999",
            "first_name": "Jane",
            "last_name": "Doe",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["cell_number"] == "+5511999999999"
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"

    db_session.refresh(user)
    assert user.profile.first_name == "Jane"


def test_get_profile_requires_authentication(client):
    response = client.get("/users/me/profile")

    assert response.status_code == 401


def test_auth_me_returns_profile_when_available(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    user.profile = UserProfile(first_name="Jane", last_name="Doe")
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["first_name"] == "Jane"
    assert data["profile"]["last_name"] == "Doe"
