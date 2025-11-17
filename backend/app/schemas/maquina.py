from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class MaquinaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=160)
    descricao: Optional[str] = None
    uom_hh_id: int = Field(..., ge=1)

class MaquinaCreate(MaquinaBase):
    pass

class MaquinaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=160)
    descricao: Optional[str] = None
    uom_hh_id: Optional[int] = Field(None, ge=1)

class MaquinaOut(MaquinaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
