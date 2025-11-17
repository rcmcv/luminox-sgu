from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

TipoHH = Literal["REGULAR", "EXTRA", "FERIADO"]

class ContratoHHPrecoBase(BaseModel):
    contrato_id: int = Field(..., ge=1)
    maquina_id: int = Field(..., ge=1)
    tipo_hh: TipoHH
    uom_id: int = Field(..., ge=1)        # normalmente a UoM "hora"
    preco_hora: float = Field(..., ge=0)

class ContratoHHPrecoCreate(ContratoHHPrecoBase):
    pass

class ContratoHHPrecoUpdate(BaseModel):
    # contrato_id e maquina_id não mudam normalmente; se precisar, podemos liberar depois
    tipo_hh: Optional[TipoHH] = None
    uom_id: Optional[int] = Field(None, ge=1)
    preco_hora: Optional[float] = Field(None, ge=0)

class ContratoHHPrecoOut(ContratoHHPrecoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
