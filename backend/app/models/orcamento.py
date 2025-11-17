from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Enum
from app.models.base import Base, IDMixin, TimeStampedMixin

TIPO_ORCAMENTO = ("CONTRATO", "SPOT")
STATUS_ORC = ("RASCUNHO", "ENVIADO", "ACEITO", "CANCELADO")

class Orcamento(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "orcamentos"

    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # CONTRATO exige contrato_id; SPOT deve ter contrato_id = NULL
    tipo: Mapped[str] = mapped_column(String(16), nullable=False, default="RASCUNHO")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="RASCUNHO")

    contrato_id: Mapped[int | None] = mapped_column(
        ForeignKey("contratos.id", ondelete="RESTRICT"), nullable=True, index=True
    )

    moeda: Mapped[str] = mapped_column(String(8), nullable=False, default="BRL")
    titulo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Totais (por enquanto manuais; no próximo passo calcularemos ao inserir itens)
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    desconto: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    acrescimo: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
