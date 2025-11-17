from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from app.models.base import Base, IDMixin, TimeStampedMixin

class User(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "users"

    # login
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)

    # segurança
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # RBAC simples (ADMIN, FINANCE, OPERACAO, VIEWER)
    role: Mapped[str] = mapped_column(String(20), default="VIEWER", nullable=False)
