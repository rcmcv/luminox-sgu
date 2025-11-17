"""
Módulo de configurações da aplicação.

- Usa Pydantic Settings para ler variáveis de ambiente.
- Em desenvolvimento, carrega .env automaticamente (se existir).
- Em produção, NÃO dependemos de .env: use variáveis de ambiente reais no servidor.
"""

from functools import lru_cache
from typing import List, Literal, Optional
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Carrega .env SOMENTE em desenvolvimento, se existir:
def _load_dotenv_if_dev() -> None:
    """
    Em dev, carregamos as variáveis do arquivo .env, caso exista.
    Em prod, não fazemos nada (evita risco de vazar segredos do repositório).
    """
    env = os.getenv("ENV", "dev").lower()
    if env != "prod":
        # Import local para evitar depender do python-dotenv em prod
        try:
            from dotenv import load_dotenv
            # only=True → não sobrepõe variáveis já definidas no ambiente
            load_dotenv(override=False)
        except Exception:
            # Se não tiver python-dotenv, apenas ignore silenciosamente
            pass

_load_dotenv_if_dev()


class Settings(BaseSettings):
    """
    Configurações principais da aplicação.
    Campos são preenchidos por variáveis de ambiente ou .env (em dev).
    """

    # Ambiente / metadados
    ENV: Literal["dev", "prod", "test"] = "dev"
    PROJECT_NAME: str = "Usinagem ERP API"
    VERSION: str = "0.1.0"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALG: str = "HS256"

    # Segurança
    SECRET_KEY: str  # gere uma chave segura e mantenha fora do Git

    # Banco de dados (adicionaremos SQLAlchemy depois)
    DATABASE_URL: str  # ex.: sqlite:///./dev.db ou postgresql+psycopg://user:pass@host/db

    # CORS: em dev pode ser *, em prod restrinja para o(s) domínio(s) do frontend
    CORS_ORIGINS: List[str] = ["*"]

    # Conveniências derivadas
    @property
    def DEBUG(self) -> bool:
        return self.ENV == "dev"

    model_config = SettingsConfigDict(
        # Não definimos env_file aqui para desencorajar uso de .env em prod.
        # O carregamento do .env em dev já é feito por _load_dotenv_if_dev().
        extra="ignore",  # ignore variáveis não mapeadas
        validate_default=True
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retorna instância singleton de Settings, com cache.
    """
    return Settings()
