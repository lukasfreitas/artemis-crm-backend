# artemis-crm-backend
artemis crm backend

## Running Tests

To run the unit tests, use the following command:

```bash
pytest tests/
```

The tests are structured as follows:
- `tests/conftest.py`: Shared fixtures for database and client setup
- `tests/api/routes/test_auth.py`: Tests for authentication endpoints
- `tests/core/test_security.py`: Tests for password hashing and verification
- `tests/models/test_user.py`: Tests for the User model

Dependencies for testing:
- pytest
- httpx
- faker
- factory-boy
