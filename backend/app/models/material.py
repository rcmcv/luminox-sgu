from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey
from app.models.base import Base, IDMixin, TimeStampedMixin

class Material(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "materiais"

    nome: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Unidade base (ex.: kg)
    uom_base_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
