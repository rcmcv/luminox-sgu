from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TipoServicoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    descricao: Optional[str] = None

class TipoServicoCreate(TipoServicoBase):
    pass

class TipoServicoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    descricao: Optional[str] = None

class TipoServicoOut(TipoServicoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
