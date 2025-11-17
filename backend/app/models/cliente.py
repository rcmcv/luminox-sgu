# Modelo simples só para testarmos migrations (CRUD virá depois)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.models.base import Base, IDMixin, TimeStampedMixin

class Cliente(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "clientes"

    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
