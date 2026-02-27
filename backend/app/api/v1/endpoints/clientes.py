from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api import ok, created
from app.deps.db import get_db
from app.deps.pagination import get_pagination
from app.repositories import cliente as cliente_repo
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteOutComContatos, ClienteUpdate

router = APIRouter()


@router.post("/clientes", status_code=status.HTTP_201_CREATED)
async def criar_cliente(
    payload: ClienteCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Cria cliente e permite criar contatos junto (1 request) via payload.contatos.
    """
    obj = await cliente_repo.create(db, payload)
    return created(obj, message="Cliente cadastrado com sucesso.")


@router.get("/clientes")
async def listar_clientes(
    nome: Optional[str] = Query(None, description="Filtro por nome (contém)"),
    cnpj: Optional[str] = Query(None, description="Filtro por CNPJ (exato)"),
    ativo: Optional[bool] = Query(None, description="Filtro por ativo/inativo"),
    include_contatos: bool = Query(False, description="Se true, retorna contatos junto"),
    pagination=Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista clientes com filtros básicos e paginação.
    """
    itens = await cliente_repo.list_(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        nome=nome,
        cnpj=cnpj,
        ativo=ativo,
    )

    # Se quiser incluir contatos, é só mudar o schema de resposta.
    # (O relacionamento em Cliente está lazy='selectin', então isso vem eficiente.)
    if include_contatos:
        return ok([ClienteOutComContatos.model_validate(x) for x in itens], meta=pagination.meta)

    return ok([ClienteOut.model_validate(x) for x in itens], meta=pagination.meta)


@router.get("/clientes/{cliente_id}")
async def obter_cliente(
    cliente_id: int,
    include_contatos: bool = Query(False, description="Se true, retorna contatos junto"),
    db: AsyncSession = Depends(get_db),
):
    obj = await cliente_repo.get(db, cliente_id)
    if not obj:
        return ok(None, message="Cliente não encontrado.", status_code=404)

    if include_contatos:
        return ok(ClienteOutComContatos.model_validate(obj))

    return ok(ClienteOut.model_validate(obj))


@router.put("/clientes/{cliente_id}")
async def atualizar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await cliente_repo.update(db, cliente_id, payload)
    if not obj:
        return ok(None, message="Cliente não encontrado.", status_code=404)

    return ok(ClienteOut.model_validate(obj), message="Cliente atualizado com sucesso.")


@router.delete("/clientes/{cliente_id}")
async def desativar_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete: ativo=false.
    Se houver vínculos (orçamentos/contratos), o repo lança HTTPException 409.
    """
    result = await cliente_repo.delete(db, cliente_id)
    if not result:
        return ok(None, message="Cliente não encontrado.", status_code=404)

    return ok(True, message="Cliente desativado com sucesso.")