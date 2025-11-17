from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.schemas.unidade_medida import UoMCreate, UoMUpdate, UoMOut
from app.repositories import unidade_medida as repo
from app.core.api import ok, created

router = APIRouter()

@router.post(
    "/unidades-medida",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_uom(
    payload: UoMCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id, "nome": obj.nome, "simbolo": obj.simbolo, "categoria": obj.categoria,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Unidade de medida criada com sucesso.", request=request)

@router.get("/unidades-medida", response_model=None)
async def list_uom(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id, "nome": i.nome, "simbolo": i.simbolo, "categoria": i.categoria,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/unidades-medida/{uom_id}", response_model=UoMOut)
async def get_uom(
    uom_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, uom_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    return obj

@router.put(
    "/unidades-medida/{uom_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_uom(
    uom_id: int,
    payload: UoMUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, uom_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    data = {
        "id": obj.id, "nome": obj.nome, "simbolo": obj.simbolo, "categoria": obj.categoria,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Unidade de medida atualizada com sucesso.", request=request)

@router.delete(
    "/unidades-medida/{uom_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_uom(
    uom_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    removed = await repo.delete(db, uom_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Unidade de medida não encontrada")
    return ok(message="Unidade de medida removida com sucesso.", data=None, request=request)
