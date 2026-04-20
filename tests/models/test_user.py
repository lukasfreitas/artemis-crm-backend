from factory import Factory
from app.models.user import User

class UserFactory(Factory):
    class Meta:
        model = User

    id = "test-id"
    email = "test@example.com"
    password_hash = "hashedpassword"
    is_active = True

def test_user_creation():
    user = UserFactory()
    assert user.email == "test@example.com"
    assert user.password_hash == "hashedpassword"
    assert user.is_active

def test_user_attributes():
    user = User(
        email="user@example.com",
        password_hash="hash123",
        is_active=False
    )
    assert user.email == "user@example.com"
    assert user.password_hash == "hash123"
    assert not user.is_active