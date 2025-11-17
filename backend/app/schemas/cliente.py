from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Observação: mantendo email como str simples por enquanto (sem EmailStr)
# para não adicionar dependências extras. Depois trocamos por EmailStr.

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    email: Optional[str] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[str] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)

class ClienteOut(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # pydantic v2: ler de ORM
