from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api import ok, created
from app.deps.db import get_db
from app.repositories import cliente_contato as contato_repo
from app.schemas.cliente_contato import (
    ClienteContatoCreate,
    ClienteContatoOut,
    ClienteContatoUpdate,
)

router = APIRouter()


@router.get("/clientes/{cliente_id}/contatos")
async def listar_contatos(
    cliente_id: int,
    ativo: Optional[bool] = Query(True, description="Por padrão lista somente ativos. Use ativo=None para todos."),
    db: AsyncSession = Depends(get_db),
):
    itens = await contato_repo.list_(db, cliente_id=cliente_id, ativo=ativo)
    return ok([ClienteContatoOut.model_validate(x) for x in itens])


@router.post("/clientes/{cliente_id}/contatos", status_code=status.HTTP_201_CREATED)
async def criar_contato(
    cliente_id: int,
    payload: ClienteContatoCreate,
    db: AsyncSession = Depends(get_db),
):
    obj = await contato_repo.create(db, cliente_id=cliente_id, data=payload)
    return created(ClienteContatoOut.model_validate(obj), message="Contato cadastrado com sucesso.")


@router.put("/clientes/{cliente_id}/contatos/{contato_id}")
async def atualizar_contato(
    cliente_id: int,
    contato_id: int,
    payload: ClienteContatoUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await contato_repo.update(db, cliente_id=cliente_id, contato_id=contato_id, data=payload)
    if not obj:
        return ok(None, message="Contato não encontrado.", status_code=404)

    return ok(ClienteContatoOut.model_validate(obj), message="Contato atualizado com sucesso.")


@router.delete("/clientes/{cliente_id}/contatos/{contato_id}")
async def desativar_contato(
    cliente_id: int,
    contato_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await contato_repo.delete(db, cliente_id=cliente_id, contato_id=contato_id)
    if not result:
        return ok(None, message="Contato não encontrado.", status_code=404)

    return ok(True, message="Contato desativado com sucesso.")