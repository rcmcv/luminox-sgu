from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from app.models.base import Base, IDMixin, TimeStampedMixin

class TipoServico(Base, IDMixin, TimeStampedMixin):
    __tablename__ = "tipos_servico"

    nome: Mapped[str] = mapped_column(String(120), nullable=False, index=True, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
