"""Model ClienteContato.

Um Cliente pode ter vários contatos (telefone/e-mail/pessoa/cargo).

Importante:
- Mantemos soft delete via campo `ativo`.
- Mesmo com soft delete, o relacionamento é útil para carregamento e integridade.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimeStampedMixin

if TYPE_CHECKING:
    from app.models.cliente import Cliente

class ClienteContato(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "cliente_contatos"

    cliente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    nome_contato: Mapped[str] = mapped_column(String(120), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    cliente: Mapped[Cliente] = relationship("Cliente", back_populates="contatos")