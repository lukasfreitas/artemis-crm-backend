from factory import Factory
from app.models.user import User
from app.models.user_profile import UserProfile

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


def test_user_profile_relationship():
    user = User(
        email="profile@example.com",
        password_hash="hash123",
        profile=UserProfile(
            cell_number="+5511999999999",
            first_name="Artemis",
            last_name="CRM",
        ),
    )

    assert user.profile.cell_number == "+5511999999999"
    assert user.profile.first_name == "Artemis"
    assert user.profile.last_name == "CRM"
