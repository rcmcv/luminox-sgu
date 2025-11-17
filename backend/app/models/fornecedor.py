from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from app.models.base import Base, IDMixin, TimeStampedMixin

class Fornecedor(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "fornecedores"

    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)   # sem validação por enquanto
    email: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contato: Mapped[str | None] = mapped_column(String(120), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
