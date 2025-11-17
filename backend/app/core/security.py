from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
settings = get_settings()

# ---- Password ----
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ---- JWT ----
def _expire_in(minutes: int = 15) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)

def _expire_in_days(days: int) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)

def create_access_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    claims = {"sub": subject, "type": "access", "exp": _expire_in(settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    if extra:
        claims.update(extra)
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALG)

def create_refresh_token(subject: str, extra: Optional[dict[str, Any]] = None) -> str:
    claims = {"sub": subject, "type": "refresh", "exp": _expire_in_days(settings.REFRESH_TOKEN_EXPIRE_DAYS)}
    if extra:
        claims.update(extra)
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALG])
