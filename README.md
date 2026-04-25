# artemis-crm-backend
artemis crm backend

## Railway

O projeto agora inclui `railway.toml` com:

- `startCommand` usando `uvicorn` em `0.0.0.0` e na porta injetada por `PORT`
- `healthcheckPath` em `/health`

O deploy nao executa criacao automatica de tabelas. Isso assume que o banco da Railway ja existe e que o schema e gerenciado fora do ciclo de deploy.

Variaveis minimas para producao:

- `DATABASE_URL`
- `SECRET_KEY`
- `FRONTEND_URL`

Use `.env.example` como referencia local.

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
