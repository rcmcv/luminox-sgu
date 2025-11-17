from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, Integer
from app.models.base import Base, IDMixin, TimeStampedMixin

class ContratoMaterialPreco(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "contrato_material_precos"

    contrato_id: Mapped[int] = mapped_column(
        ForeignKey("contratos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materiais.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # normalmente "kg", mas deixamos flexível
    uom_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    preco_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("contrato_id", "material_id", name="uq_contrato_material"),
    )
