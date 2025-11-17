from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.core.api import ok, created
from app.repositories import contrato_hh_preco as repo
from app.schemas.contrato_hh_preco import (
    ContratoHHPrecoCreate, ContratoHHPrecoUpdate, ContratoHHPrecoOut
)

router = APIRouter()

# CREATE (contrato escopado na rota)
@router.post(
    "/contratos/{contrato_id}/hh-precos",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_contrato_hh_preco(
    contrato_id: int,
    payload: ContratoHHPrecoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Garante que usaremos o contrato_id da rota (ignora o que vier no body)
    data = ContratoHHPrecoCreate(
        contrato_id=contrato_id,
        maquina_id=payload.maquina_id,
        tipo_hh=payload.tipo_hh,
        uom_id=payload.uom_id,
        preco_hora=payload.preco_hora,
    )
    obj = await repo.create(db, data)
    out = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "maquina_id": obj.maquina_id,
        "tipo_hh": obj.tipo_hh,
        "uom_id": obj.uom_id,
        "preco_hora": float(obj.preco_hora),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=out, message="Preço de HH por máquina criado com sucesso.", request=request)

# LIST (sempre por contrato; filtros opcionais)
@router.get("/contratos/{contrato_id}/hh-precos", response_model=None)
async def list_contrato_hh_precos(
    contrato_id: int,
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    maquina_id: int | None = Query(None, ge=1),
    tipo_hh: str | None = Query(None),
):
    items = await repo.list_(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        contrato_id=contrato_id,
        maquina_id=maquina_id,
        tipo_hh=tipo_hh
    )
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "contrato_id": i.contrato_id,
            "maquina_id": i.maquina_id,
            "tipo_hh": i.tipo_hh,
            "uom_id": i.uom_id,
            "preco_hora": float(i.preco_hora),
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

# GET by id (também aninhado em contrato para evitar colisão)
@router.get("/contratos/{contrato_id}/hh-precos/{preco_id}", response_model=ContratoHHPrecoOut)
async def get_contrato_hh_preco(
    contrato_id: int,
    preco_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    return obj

# UPDATE
@router.put(
    "/contratos/{contrato_id}/hh-precos/{preco_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_contrato_hh_preco(
    contrato_id: int,
    preco_id: int,
    payload: ContratoHHPrecoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    obj = await repo.update(db, preco_id, payload)
    out = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "maquina_id": obj.maquina_id,
        "tipo_hh": obj.tipo_hh,
        "uom_id": obj.uom_id,
        "preco_hora": float(obj.preco_hora),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=out, message="Preço de HH por máquina atualizado com sucesso.", request=request)

# DELETE
@router.delete(
    "/contratos/{contrato_id}/hh-precos/{preco_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_contrato_hh_preco(
    contrato_id: int,
    preco_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    removed = await repo.delete(db, preco_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Preço de HH de contrato não encontrado")
    return ok(message="Preço de HH por máquina removido com sucesso.", data=None, request=request)
