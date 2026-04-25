from faker import Faker
from app.models.user import User
from app.core.security import hash_password

faker = Faker()

def test_register_success(client, db_session):
    email = faker.email()
    response = client.post("/auth/register", json={
        "email": email,
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert data["is_active"] is True

def test_register_existing_email(client, db_session):
    email = faker.email()
    existing_user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(existing_user)
    db_session.commit()

    response = client.post("/auth/register", json={
        "email": email,
        "password": "password123"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Email já cadastrado"

def test_login_success(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email

def test_login_invalid_credentials(client, db_session):
    response = client.post("/auth/login", json={
        "email": faker.email(),
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"

def test_me_endpoint(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })

    token = login_response.json()["access_token"]
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["id"] == user.id
    assert data["is_active"] is True


def test_me_endpoint_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"


def test_refresh_success(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })

    refresh_response = client.post("/auth/refresh", json={
        "refresh_token": login_response.json()["refresh_token"]
    })

    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["refresh_token"] != login_response.json()["refresh_token"]
    assert data["user"]["email"] == email


def test_refresh_revoked_session(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 204

    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"] == "Sessão revogada"


def test_logout_revokes_session(client, db_session):
    email = faker.email()
    user = User(email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "password123"
    })

    logout_response = client.post("/auth/logout", json={
        "refresh_token": login_response.json()["refresh_token"]
    })

    assert logout_response.status_code == 204
