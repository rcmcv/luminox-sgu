from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Numeric, UniqueConstraint, Integer
from app.models.base import Base, IDMixin, TimeStampedMixin

# Tipos de hora: REGULAR | EXTRA | FERIADO
TIPO_HH_REGULAR = "REGULAR"
TIPO_HH_EXTRA = "EXTRA"
TIPO_HH_FERIADO = "FERIADO"
TIPOS_HH = (TIPO_HH_REGULAR, TIPO_HH_EXTRA, TIPO_HH_FERIADO)

class ContratoHHPreco(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "contrato_hh_precos"

    contrato_id: Mapped[int] = mapped_column(
        ForeignKey("contratos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    maquina_id: Mapped[int] = mapped_column(
        ForeignKey("maquinas.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # REGULAR | EXTRA | FERIADO
    tipo_hh: Mapped[str] = mapped_column(String(16), nullable=False)

    # Preço por hora (moeda segue o contrato; aqui guardamos apenas o número)
    preco_hora: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # UoM da hora (normalmente "h"); vinculado para consistência
    uom_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    __table_args__ = (
        UniqueConstraint("contrato_id", "maquina_id", "tipo_hh", name="uq_contrato_maquina_tipo"),
    )
