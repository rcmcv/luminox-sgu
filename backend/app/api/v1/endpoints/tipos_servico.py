from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.schemas.tipo_servico import TipoServicoCreate, TipoServicoUpdate, TipoServicoOut
from app.repositories import tipo_servico as repo
from app.core.api import ok, created

router = APIRouter()

@router.post(
    "/tipos-servico",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_tipo_servico(
    payload: TipoServicoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id, "nome": obj.nome, "descricao": obj.descricao,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Tipo de Serviço criado com sucesso.", request=request)

@router.get("/tipos-servico", response_model=None)
async def list_tipos_servico(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id, "nome": i.nome, "descricao": i.descricao,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/tipos-servico/{tipo_id}", response_model=TipoServicoOut)
async def get_tipo_servico(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, tipo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de Serviço não encontrado")
    return obj

@router.put(
    "/tipos-servico/{tipo_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_tipo_servico(
    tipo_id: int,
    payload: TipoServicoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, tipo_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de Serviço não encontrado")
    data = {
        "id": obj.id, "nome": obj.nome, "descricao": obj.descricao,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Tipo de Serviço atualizado com sucesso.", request=request)

@router.delete(
    "/tipos-servico/{tipo_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_tipo_servico(
    tipo_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ok_del = await repo.delete(db, tipo_id)
    if not ok_del:
        raise HTTPException(status_code=404, detail="Tipo de Serviço não encontrado")
    return ok(message="Tipo de Serviço removido com sucesso.", data=None, request=request)
