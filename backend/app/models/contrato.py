from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Text, Boolean, Date, Numeric
from app.models.base import Base, IDMixin, TimeStampedMixin

class Contrato(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "contratos"

    # vínculo
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        index=True, nullable=False
    )

    # vigência
    data_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_fim:    Mapped[date | None] = mapped_column(Date, nullable=True)

    # status / meta
    moeda: Mapped[str] = mapped_column(String(8), default="BRL", nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # DEFAULTS de preços (fallback)
    hh_regular_default: Mapped[float | None]  = mapped_column(Numeric(12, 2), nullable=True)
    hh_extra_default:   Mapped[float | None]  = mapped_column(Numeric(12, 2), nullable=True)
    hh_feriado_default: Mapped[float | None]  = mapped_column(Numeric(12, 2), nullable=True)
    material_kg_default: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
