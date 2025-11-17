from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, StrictInt

TipoOrc = Literal["CONTRATO", "SPOT"]
StatusOrc = Literal["RASCUNHO", "ENVIADO", "ACEITO", "CANCELADO"]

class OrcamentoBase(BaseModel):
    cliente_id: StrictInt = Field(..., ge=1, description="ID do cliente (>= 1)")
    tipo: TipoOrc = "SPOT"
    status: StatusOrc = "RASCUNHO"
    contrato_id: Optional[int] = None
    moeda: str = Field("BRL", min_length=1, max_length=8)
    titulo: Optional[str] = Field(None, max_length=120)
    observacoes: Optional[str] = None

    subtotal: float = 0.0
    desconto: float = 0.0
    acrescimo: float = 0.0
    total: float = 0.0

class OrcamentoCreate(OrcamentoBase):
    pass

class OrcamentoUpdate(BaseModel):
    # atualização parcial
    cliente_id: Optional[int] = Field(None, ge=1)
    tipo: Optional[TipoOrc] = None
    status: Optional[StatusOrc] = None
    contrato_id: Optional[int] = None
    moeda: Optional[str] = Field(None, min_length=1, max_length=8)
    titulo: Optional[str] = Field(None, max_length=120)
    observacoes: Optional[str] = None

    subtotal: Optional[float] = Field(None, ge=0)
    desconto: Optional[float] = Field(None, ge=0)
    acrescimo: Optional[float] = Field(None, ge=0)
    total: Optional[float] = Field(None, ge=0)

class OrcamentoOut(OrcamentoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
