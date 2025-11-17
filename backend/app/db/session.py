# Sessão assíncrona da aplicação (Alembic continua sync)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.settings import get_settings

settings = get_settings()

def _to_async_url(url: str) -> str:
    """
    Converte URL sync -> async para drivers suportados.
    - SQLite: sqlite:/// -> sqlite+aiosqlite:///
    - Postgres: postgresql+psycopg:// -> postgresql+asyncpg://
    """
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
    if url.startswith("postgresql://"):
        # caso o dev use postgresql:// (psycopg implícito)
        return url.replace("postgresql://", "postgresql+asyncpg://")
    # adicionar outros mapeamentos se necessário
    return url

ASYNC_DATABASE_URL = _to_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
