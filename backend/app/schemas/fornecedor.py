from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FornecedorBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    cnpj: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)
    contato: Optional[str] = Field(None, max_length=120)
    observacoes: Optional[str] = None

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    cnpj: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)
    contato: Optional[str] = Field(None, max_length=120)
    observacoes: Optional[str] = None

class FornecedorOut(FornecedorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
