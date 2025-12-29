# Usinagem (monorepo)

Repositório **monorepo** com:
- **backend/** (FastAPI + SQLAlchemy + Alembic + JWT)
- **frontend/** (React/Vite/Tailwind — será iniciado em breve)

## Estrutura

luminox-sgu/
├─ backend/ # API FastAPI + DB + migrações
│ ├─ app/
│ ├─ alembic/
│ ├─ alembic.ini
│ └─ requirements.txt
└─ frontend/ # App web (React/Vite) — a iniciar


## Requisitos

- **Python 3.11+**
- **Git**
- (Opcional) **Node.js 18+** para o frontend
- (Opcional) VS Code

## Como rodar o backend (dev)

> Sempre execute os comandos **de dentro de `backend/`**.

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt

# Windows
copy .env.example .env
# Linux/macOS
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload

# Swagger

http://127.0.0.1:8000/docs

#Variáveis de ambiente (backend/.env)

ENV=dev
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=***gerar_com_secrets***
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Gerar SECRET (exemplo):

python -c "import secrets; print(secrets.token_urlsafe(32))"

# Convenções
#Commits (sugestões):

- 🧾 Orçamentos: itens HH/MATERIAL/LIVRE com totais
- 🛡️ Auth: RBAC + JWT refresh
- 🧱 Estrutura: monorepo (backend/ + frontend/)
- 🔧 Fix: validações de contrato_id

# Padrões de API:

- Envelopes com success, message, data, meta, request_id
- Erros padronizados (422/400/409/500) com mensagens amigáveis

# VS Code (opcional)

Crie .vscode/launch.json na raiz para rodar Uvicorn já apontando para backend/:

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend: Uvicorn",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}

# Git remoto

git remote -v
git remote set-url origin https://github.com/rcmcv/usinagem.git

#Próximos passos

- Iniciar frontend/ (Vite + React + Tailwind)
- Telas de Orçamentos (CONTRATO/SPOT) + itens
- Deploy (Render/Railway/VPS) com gunicorn/uvicorn + nginx
- Seeds de dados para ambiente de testes
