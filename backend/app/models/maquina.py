from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey
from app.models.base import Base, IDMixin, TimeStampedMixin

class Maquina(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "maquinas"

    nome: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Unidade de hora-homem (ex.: hora)
    uom_hh_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
