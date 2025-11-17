from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ContratoMaterialPrecoBase(BaseModel):
    contrato_id: int = Field(..., ge=1)
    material_id: int = Field(..., ge=1)
    uom_id: int = Field(..., ge=1)            # normalmente UoM do material (ex.: kg)
    preco_unitario: float = Field(..., ge=0)

class ContratoMaterialPrecoCreate(ContratoMaterialPrecoBase):
    pass

class ContratoMaterialPrecoUpdate(BaseModel):
    uom_id: Optional[int] = Field(None, ge=1)
    preco_unitario: Optional[float] = Field(None, ge=0)

class ContratoMaterialPrecoOut(ContratoMaterialPrecoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
