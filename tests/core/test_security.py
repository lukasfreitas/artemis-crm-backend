from app.core.security import hash_password, verify_password

def test_hash_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_verify_password_correct():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)

def test_verify_password_incorrect():
    password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed = hash_password(password)
    assert not verify_password(wrong_password, hashed)