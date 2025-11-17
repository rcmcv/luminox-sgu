from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.api import ok
from app.deps.pagination import get_pagination

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.repositories import cliente as repo

router = APIRouter()

@router.post(
    "/clientes",
    response_model=ClienteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_cliente(payload: ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await repo.create(db, payload)

@router.get("/clientes", response_model=None)  # removemos o response_model para não “brigar” com o envelope
async def list_clientes(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    return ok(data=[  # convertemos para dict simples (Pydantic model -> dict) via from_attributes já funciona, mas aqui garantimos
        {
            "id": i.id,
            "nome": i.nome,
            "email": i.email,
            "telefone": i.telefone,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ], meta=meta, request=request)

@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
async def get_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return obj

@router.put(
    "/clientes/{cliente_id}",
    response_model=ClienteOut,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, cliente_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return obj

@router.delete(
    "/clientes/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db),
):
    ok = await repo.delete(db, cliente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return None
