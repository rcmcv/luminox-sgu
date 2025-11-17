from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class UoMBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    simbolo: str = Field(..., min_length=1, max_length=16)
    categoria: Optional[str] = Field(None, max_length=60)

class UoMCreate(UoMBase):
    pass

class UoMUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=120)
    simbolo: Optional[str] = Field(None, min_length=1, max_length=16)
    categoria: Optional[str] = Field(None, max_length=60)

class UoMOut(UoMBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
