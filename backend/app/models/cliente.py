"""Model Cliente.

Evoluído para armazenar os dados cadastrais completos que vão para:
- Orçamentos/PDF
- E-mails de aprovação

Observação importante:
O projeto utiliza *soft delete* (campo `ativo`). Portanto, o DELETE na API
desativa o registro ao invés de apagar fisicamente do banco.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, text

from app.models.base import Base, IDMixin, TimeStampedMixin

if TYPE_CHECKING:
    from app.models.cliente_contato import ClienteContato

class Cliente(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "clientes"

    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    # Campos legados (mantidos por compatibilidade; no futuro, contatos ficam em ClienteContato)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Dados cadastrais completos (para PDF / aprovação)
    cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    ie: Mapped[str | None] = mapped_column(String(30), nullable=True)

    endereco_logradouro: Mapped[str | None] = mapped_column(String(180), nullable=True)
    endereco_numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(80), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(2), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(12), nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete
    ativo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    # Relacionamento 1:N com contatos
    contatos: Mapped[list[ClienteContato]] = relationship(
        "ClienteContato",
        back_populates="cliente",
        cascade="all, delete-orphan",
        lazy="selectin",
    )