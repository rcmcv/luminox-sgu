"""
Schemas de ClienteContato (Pydantic).

Um Cliente pode ter vários contatos (nome, cargo, email, telefone...).
Nesta etapa, criamos os schemas necessários para:
- criar / atualizar contato
- retornar contato (com timestamps)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ClienteContatoBase(BaseModel):
    nome_contato: str = Field(..., min_length=2, max_length=120)
    cargo: Optional[str] = Field(None, max_length=120)
    email: Optional[EmailStr] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)
    observacoes: Optional[str] = None
    ativo: bool = True


class ClienteContatoCreate(ClienteContatoBase):
    """Payload para criar contato."""
    pass


class ClienteContatoUpdate(BaseModel):
    """Payload para atualizar contato (parcial)."""
    nome_contato: Optional[str] = Field(None, min_length=2, max_length=120)
    cargo: Optional[str] = Field(None, max_length=120)
    email: Optional[EmailStr] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class ClienteContatoOut(ClienteContatoBase):
    """Resposta de contato."""
    id: int
    cliente_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True