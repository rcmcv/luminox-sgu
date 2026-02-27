"""
Schemas de Cliente (Pydantic).

O Cliente alimenta:
- Orçamentos/PDF
- E-mail de aprovação

Nesta etapa, o schema passa a suportar:
- dados cadastrais completos
- soft delete via campo `ativo`
- criação do cliente com contatos em 1 request
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.cliente_contato import ClienteContatoCreate, ClienteContatoOut


class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)

    # Campos legados (mantidos para compatibilidade)
    email: Optional[EmailStr] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)

    # Dados cadastrais completos
    cnpj: Optional[str] = Field(None, max_length=20)
    ie: Optional[str] = Field(None, max_length=30)

    endereco_logradouro: Optional[str] = Field(None, max_length=180)
    endereco_numero: Optional[str] = Field(None, max_length=20)

    bairro: Optional[str] = Field(None, max_length=80)
    cidade: Optional[str] = Field(None, max_length=80)
    estado: Optional[str] = Field(None, max_length=2, description="UF (ex.: CE, SP)")
    cep: Optional[str] = Field(None, max_length=12)

    observacoes: Optional[str] = None
    ativo: bool = True


class ClienteCreate(ClienteBase):
    """
    Payload para criar cliente.
    Permite enviar contatos já na criação, em 1 request.
    """
    contatos: List[ClienteContatoCreate] = Field(default_factory=list)


class ClienteUpdate(BaseModel):
    """
    Payload para atualizar cliente (parcial).
    (Não mexe em contatos aqui; contatos terão sub-recurso na API.)
    """
    nome: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = Field(None, max_length=180)
    telefone: Optional[str] = Field(None, max_length=40)

    cnpj: Optional[str] = Field(None, max_length=20)
    ie: Optional[str] = Field(None, max_length=30)

    endereco_logradouro: Optional[str] = Field(None, max_length=180)
    endereco_numero: Optional[str] = Field(None, max_length=20)

    bairro: Optional[str] = Field(None, max_length=80)
    cidade: Optional[str] = Field(None, max_length=80)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=12)

    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class ClienteOut(ClienteBase):
    """Resposta padrão de Cliente (sem obrigar contatos)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClienteOutComContatos(ClienteOut):
    """Resposta de Cliente incluindo a lista de contatos."""
    contatos: List[ClienteContatoOut] = Field(default_factory=list)