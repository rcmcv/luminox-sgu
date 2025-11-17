# Define a Base declarativa e mixins comuns (id, timestamps)
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, Integer

class Base(DeclarativeBase):
    pass

class TimeStampedMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
