from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.models.base import Base, IDMixin, TimeStampedMixin

class UnidadeMedida(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "unidades_medida"

    # Ex.: "Hora", "Quilograma", "Unidade"
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    # Ex.: "h", "kg", "un"
    simbolo: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    # Ex.: "tempo", "massa", "quantidade" (opcional, só para organização)
    categoria: Mapped[str | None] = mapped_column(String(60), nullable=True)
