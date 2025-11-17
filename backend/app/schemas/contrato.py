from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

class ContratoBase(BaseModel):
    cliente_id: int = Field(..., ge=1)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    moeda: str = Field("BRL", min_length=1, max_length=8)
    ativo: bool = True
    observacoes: Optional[str] = None

    hh_regular_default: Optional[float] = Field(None, ge=0)
    hh_extra_default: Optional[float] = Field(None, ge=0)
    hh_feriado_default: Optional[float] = Field(None, ge=0)
    material_kg_default: Optional[float] = Field(None, ge=0)

class ContratoCreate(ContratoBase):
    pass

class ContratoUpdate(BaseModel):
    cliente_id: Optional[int] = Field(None, ge=1)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    moeda: Optional[str] = Field(None, min_length=1, max_length=8)
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None

    hh_regular_default: Optional[float] = Field(None, ge=0)
    hh_extra_default: Optional[float] = Field(None, ge=0)
    hh_feriado_default: Optional[float] = Field(None, ge=0)
    material_kg_default: Optional[float] = Field(None, ge=0)

class ContratoOut(ContratoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
