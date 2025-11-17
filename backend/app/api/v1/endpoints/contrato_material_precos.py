from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.core.api import ok, created
from app.repositories import contrato_material_preco as repo
from app.schemas.contrato_material_preco import (
    ContratoMaterialPrecoCreate, ContratoMaterialPrecoUpdate, ContratoMaterialPrecoOut
)

router = APIRouter()

@router.post(
    "/contratos/{contrato_id}/material-precos",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_contrato_material_preco(
    contrato_id: int,
    payload: ContratoMaterialPrecoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    data = ContratoMaterialPrecoCreate(
        contrato_id=contrato_id,
        material_id=payload.material_id,
        uom_id=payload.uom_id,
        preco_unitario=payload.preco_unitario,
    )
    obj = await repo.create(db, data)
    out = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "material_id": obj.material_id,
        "uom_id": obj.uom_id,
        "preco_unitario": float(obj.preco_unitario),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=out, message="Preço de material do contrato criado com sucesso.", request=request)

@router.get("/contratos/{contrato_id}/material-precos", response_model=None)
async def list_contrato_material_precos(
    contrato_id: int,
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    material_id: int | None = Query(None, ge=1),
):
    items = await repo.list_(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        contrato_id=contrato_id,
        material_id=material_id
    )
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "contrato_id": i.contrato_id,
            "material_id": i.material_id,
            "uom_id": i.uom_id,
            "preco_unitario": float(i.preco_unitario),
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/contratos/{contrato_id}/material-precos/{preco_id}", response_model=ContratoMaterialPrecoOut)
async def get_contrato_material_preco(
    contrato_id: int,
    preco_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de material de contrato não encontrado")
    return obj

@router.put(
    "/contratos/{contrato_id}/material-precos/{preco_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_contrato_material_preco(
    contrato_id: int,
    preco_id: int,
    payload: ContratoMaterialPrecoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de material de contrato não encontrado")
    obj = await repo.update(db, preco_id, payload)
    out = {
        "id": obj.id,
        "contrato_id": obj.contrato_id,
        "material_id": obj.material_id,
        "uom_id": obj.uom_id,
        "preco_unitario": float(obj.preco_unitario),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=out, message="Preço de material do contrato atualizado com sucesso.", request=request)

@router.delete(
    "/contratos/{contrato_id}/material-precos/{preco_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_contrato_material_preco(
    contrato_id: int,
    preco_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.get(db, preco_id)
    if not obj or obj.contrato_id != contrato_id:
        raise HTTPException(status_code=404, detail="Preço de material de contrato não encontrado")
    removed = await repo.delete(db, preco_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Preço de material de contrato não encontrado")
    return ok(message="Preço de material do contrato removido com sucesso.", data=None, request=request)
