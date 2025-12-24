
---

# README do backend (`backend/README.md`)
```markdown
# Backend — FastAPI (Usinagem)

API para gestão de usinagem: clientes, contratos, materiais, máquinas, **orçamentos (CONTRATO/SPOT)** e itens de orçamento.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy (async) + Alembic
- Pydantic v2
- Auth: JWT (access/refresh), hash de senha com passlib[bcrypt]
- SQLite (dev) — pode trocar para Postgres depois

## Setup

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env          (Windows) | cp .env.example .env (Linux/macOS)

# criar/atualizar DB
alembic upgrade head

# subir API
uvicorn app.main:app --reload

Swagger
-------
http://127.0.0.1:8000/docs

.env (exemplo)
--------------
ENV=dev
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=coloque_uma_secret_gerada
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

Gere a SECRET com:
python -c "import secrets; print(secrets.token_urlsafe(32))"

Comandos úteis
--------------
alembic revision -m "mensagem" --autogenerate
alembic upgrade head
uvicorn app.main:app --reload

Pastas principais
-----------------
backend/
├─ app/
│  ├─ api/v1/endpoints/     # rotas (auth, users, clientes, contratos, orcamentos, itens...)
│  ├─ core/                 # config, segurança, error handlers, responses
│  ├─ deps/                 # dependências (db/session, auth, paginação)
│  ├─ models/               # SQLAlchemy models
│  ├─ repositories/         # regra de negócio/DB
│  ├─ schemas/              # Pydantic
│  ├─ services/             # resolvers de preço, etc.
│  └─ main.py               # FastAPI app
├─ alembic/                 # migrações
├─ alembic.ini
└─ requirements.txt

RBAC (papéis)
-------------
- ADMIN: tudo
- OPERACAO: cria/edita orçamentos e itens
- VIEWER: leitura
