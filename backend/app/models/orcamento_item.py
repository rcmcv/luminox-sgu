from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Numeric, Integer
from app.models.base import Base, IDMixin, TimeStampedMixin

TIPOS_ITEM = ("HH", "MATERIAL", "LIVRE")

class OrcamentoItem(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "orcamento_itens"

    orcamento_id: Mapped[int] = mapped_column(
        ForeignKey("orcamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # HH | MATERIAL | LIVRE
    item_tipo: Mapped[str] = mapped_column(String(16), nullable=False)

    # HH
    maquina_id: Mapped[int | None] = mapped_column(
        ForeignKey("maquinas.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    tipo_hh: Mapped[str | None] = mapped_column(String(16), nullable=True)  # REGULAR|EXTRA|FERIADO

    # MATERIAL
    material_id: Mapped[int | None] = mapped_column(
        ForeignKey("materiais.id", ondelete="RESTRICT"), nullable=True, index=True
    )

    # LIVRE / rótulo do item
    descricao: Mapped[str | None] = mapped_column(String(180), nullable=True)

    # UoM e quantidade (ex.: h, kg, un)
    uom_id: Mapped[int | None] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False, default=1)

    # Snapshot de preço e total do item
    preco_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_item: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
