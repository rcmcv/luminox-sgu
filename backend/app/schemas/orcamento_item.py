from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, StrictInt, StrictFloat

TipoItem = Literal["HH", "MATERIAL", "LIVRE"]
TipoHH = Literal["REGULAR", "EXTRA", "FERIADO"]

class OrcamentoItemBase(BaseModel):
    item_tipo: TipoItem
    # HH
    maquina_id: Optional[StrictInt] = Field(None, ge=1)
    tipo_hh: Optional[TipoHH] = None
    # MATERIAL
    material_id: Optional[StrictInt] = Field(None, ge=1)
    # LIVRE
    descricao: Optional[str] = Field(None, max_length=180)

    uom_id: Optional[StrictInt] = Field(None, ge=1)
    quantidade: StrictFloat = Field(1, ge=0)

    # Preço unitário só é obrigatório em LIVRE (para SPOT);
    # Para CONTRATO/HH|MATERIAL será resolvido no backend.
    preco_unitario: Optional[StrictFloat] = Field(None, ge=0)

class OrcamentoItemCreate(OrcamentoItemBase):
    pass

class OrcamentoItemUpdate(BaseModel):
    # atualização parcial
    item_tipo: Optional[TipoItem] = None
    maquina_id: Optional[StrictInt] = Field(None, ge=1)
    tipo_hh: Optional[TipoHH] = None
    material_id: Optional[StrictInt] = Field(None, ge=1)
    descricao: Optional[str] = Field(None, max_length=180)
    uom_id: Optional[StrictInt] = Field(None, ge=1)
    quantidade: Optional[StrictFloat] = Field(None, ge=0)
    preco_unitario: Optional[StrictFloat] = Field(None, ge=0)

class OrcamentoItemOut(OrcamentoItemBase):
    id: int
    orcamento_id: int
    total_item: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
