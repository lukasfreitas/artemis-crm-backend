# artemis-crm-backend
artemis crm backend

## Comandos principais

Instalar dependencias com Poetry, sem instalar o projeto como pacote:

```bash
poetry install --no-root
```

Rodar a API localmente:

```bash
poetry run uvicorn app.main:app --reload
```

## Docker

Subir a API com PostgreSQL local:

```bash
docker compose up --build
```

A API ficara disponivel em:

```bash
http://localhost:8000
```

O Compose executa `alembic upgrade head` antes de iniciar a API. Para rodar comandos dentro do container:

```bash
docker compose exec api alembic current
docker compose exec api python create_superuser.py --email admin@example.com
```

Parar os containers:

```bash
docker compose down
```

Remover tambem o volume local do PostgreSQL:

```bash
docker compose down -v
```

Verificar a URL do banco carregada no terminal:

```bash
echo $DATABASE_URL
```

Executar testes:

```bash
poetry run pytest tests/
```

Validar sintaxe de um script Python:

```bash
poetry run python -m py_compile create_superuser.py
```

## Variaveis de ambiente

Variaveis minimas para rodar o projeto:

- `DATABASE_URL`
- `SECRET_KEY`
- `FRONTEND_URL`

Quando estiver rodando comandos localmente contra o banco da Railway, use a URL publica do banco no `.env`. A URL internal/private da Railway so resolve dentro da rede da Railway.

## Railway

O projeto agora inclui `railway.toml` com:

- `startCommand` usando `uvicorn` em `0.0.0.0` e na porta injetada por `PORT`
- `healthcheckPath` em `/health`

O deploy nao executa criacao automatica de tabelas. Isso assume que o banco da Railway ja existe e que o schema e gerenciado fora do ciclo de deploy.

Use `.env.example` como referencia local.

## Migracoes com Alembic

O projeto agora possui estrutura Alembic versionada em `alembic/`.

Verificar migration atual do banco:

```bash
poetry run alembic current
```

Listar a ultima migration conhecida pelo projeto:

```bash
poetry run alembic heads
```

Ver historico de migrations:

```bash
poetry run alembic history
```

Para aplicar migracoes em um banco novo:

```bash
poetry run alembic upgrade head
```

Para gerar uma nova migration depois de alterar os models:

```bash
poetry run alembic revision --autogenerate -m "descricao da mudanca"
```

Depois de gerar uma migration, revise o arquivo criado em `alembic/versions/` antes de aplicar no banco.

Para um banco que ja existia antes do Alembic e ja esta com o schema antigo deste projeto:

```bash
poetry run alembic stamp 20260425_01
poetry run alembic upgrade head
```

Esse fluxo marca o banco existente como baseline e depois aplica apenas a migration seguinte, que adiciona `is_admin`.

## Superusuario

Para criar um usuario administrador:

```bash
poetry run python create_superuser.py --email admin@example.com
```

Ou informando a senha na linha de comando:

```bash
poetry run python create_superuser.py --email admin@example.com --password sua-senha-forte
```

O script apenas cria o registro. Ele assume que as migrations do Alembic ja foram aplicadas e que a coluna `is_admin` existe na tabela `users`.

Se nao for capaz de criar o usuario, o script retorna exit code `1` e imprime um log estruturado em JSON.

## Running Tests

To run the unit tests, use the following command:

```bash
poetry run pytest tests/
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
