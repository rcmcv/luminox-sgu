from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.schemas.contrato import ContratoCreate, ContratoUpdate, ContratoOut
from app.repositories import contrato as repo
from app.core.api import ok, created

router = APIRouter()

@router.post(
    "/contratos",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_contrato(
    payload: ContratoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id,
        "cliente_id": obj.cliente_id,
        "data_inicio": obj.data_inicio.isoformat() if obj.data_inicio else None,
        "data_fim": obj.data_fim.isoformat() if obj.data_fim else None,
        "moeda": obj.moeda,
        "ativo": obj.ativo,
        "observacoes": obj.observacoes,
        "hh_regular_default": float(obj.hh_regular_default) if obj.hh_regular_default is not None else None,
        "hh_extra_default": float(obj.hh_extra_default) if obj.hh_extra_default is not None else None,
        "hh_feriado_default": float(obj.hh_feriado_default) if obj.hh_feriado_default is not None else None,
        "material_kg_default": float(obj.material_kg_default) if obj.material_kg_default is not None else None,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Contrato criado com sucesso.", request=request)

@router.get("/contratos", response_model=None)
async def list_contratos(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    cliente_id: int | None = Query(None, ge=1),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit, cliente_id=cliente_id)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "cliente_id": i.cliente_id,
            "data_inicio": i.data_inicio.isoformat() if i.data_inicio else None,
            "data_fim": i.data_fim.isoformat() if i.data_fim else None,
            "moeda": i.moeda,
            "ativo": i.ativo,
            "observacoes": i.observacoes,
            "hh_regular_default": float(i.hh_regular_default) if i.hh_regular_default is not None else None,
            "hh_extra_default": float(i.hh_extra_default) if i.hh_extra_default is not None else None,
            "hh_feriado_default": float(i.hh_feriado_default) if i.hh_feriado_default is not None else None,
            "material_kg_default": float(i.material_kg_default) if i.material_kg_default is not None else None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/contratos/{contrato_id}", response_model=ContratoOut)
async def get_contrato(
    contrato_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, contrato_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return obj

@router.put(
    "/contratos/{contrato_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_contrato(
    contrato_id: int,
    payload: ContratoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, contrato_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    data = {
        "id": obj.id,
        "cliente_id": obj.cliente_id,
        "data_inicio": obj.data_inicio.isoformat() if obj.data_inicio else None,
        "data_fim": obj.data_fim.isoformat() if obj.data_fim else None,
        "moeda": obj.moeda,
        "ativo": obj.ativo,
        "observacoes": obj.observacoes,
        "hh_regular_default": float(obj.hh_regular_default) if obj.hh_regular_default is not None else None,
        "hh_extra_default": float(obj.hh_extra_default) if obj.hh_extra_default is not None else None,
        "hh_feriado_default": float(obj.hh_feriado_default) if obj.hh_feriado_default is not None else None,
        "material_kg_default": float(obj.material_kg_default) if obj.material_kg_default is not None else None,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Contrato atualizado com sucesso.", request=request)

@router.delete(
    "/contratos/{contrato_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_contrato(
    contrato_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    removed = await repo.delete(db, contrato_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return ok(message="Contrato removido com sucesso.", data=None, request=request)
