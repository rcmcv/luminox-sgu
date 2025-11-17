from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.core.api import ok, created
from app.schemas.orcamento_item import OrcamentoItemCreate, OrcamentoItemUpdate, OrcamentoItemOut
from app.repositories import orcamento_item as repo

router = APIRouter()

@router.post(
    "/orcamentos/{orcamento_id}/itens",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_orc_item(
    orcamento_id: int,
    payload: OrcamentoItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, orcamento_id, payload)
    return created(
        data={
            "id": obj.id,
            "orcamento_id": obj.orcamento_id,
            "item_tipo": obj.item_tipo,
            "maquina_id": obj.maquina_id,
            "tipo_hh": obj.tipo_hh,
            "material_id": obj.material_id,
            "descricao": obj.descricao,
            "uom_id": obj.uom_id,
            "quantidade": float(obj.quantidade),
            "preco_unitario": float(obj.preco_unitario),
            "total_item": float(obj.total_item),
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        },
        message="Item adicionado ao orçamento.",
        request=request,
    )

@router.get("/orcamentos/{orcamento_id}/itens", response_model=None)
async def list_orc_itens(
    orcamento_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    items = await repo.list_(db, orcamento_id)
    data = [
        {
            "id": i.id,
            "orcamento_id": i.orcamento_id,
            "item_tipo": i.item_tipo,
            "maquina_id": i.maquina_id,
            "tipo_hh": i.tipo_hh,
            "material_id": i.material_id,
            "descricao": i.descricao,
            "uom_id": i.uom_id,
            "quantidade": float(i.quantidade),
            "preco_unitario": float(i.preco_unitario),
            "total_item": float(i.total_item),
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, request=request)

@router.get("/orcamentos/{orcamento_id}/itens/{item_id}", response_model=OrcamentoItemOut)
async def get_orc_item(
    orcamento_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, item_id)
    if not obj or obj.orcamento_id != orcamento_id:
        raise HTTPException(status_code=404, detail="Item de orçamento não encontrado")
    return obj

@router.put(
    "/orcamentos/{orcamento_id}/itens/{item_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_orc_item(
    orcamento_id: int,
    item_id: int,
    payload: OrcamentoItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, orcamento_id, item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Item de orçamento não encontrado")
    return ok(
        data={
            "id": obj.id,
            "orcamento_id": obj.orcamento_id,
            "item_tipo": obj.item_tipo,
            "maquina_id": obj.maquina_id,
            "tipo_hh": obj.tipo_hh,
            "material_id": obj.material_id,
            "descricao": obj.descricao,
            "uom_id": obj.uom_id,
            "quantidade": float(obj.quantidade),
            "preco_unitario": float(obj.preco_unitario),
            "total_item": float(obj.total_item),
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        },
        message="Item do orçamento atualizado.",
        request=request,
    )

@router.delete(
    "/orcamentos/{orcamento_id}/itens/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_orc_item(
    orcamento_id: int,
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    removed = await repo.delete(db, orcamento_id, item_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Item de orçamento não encontrado")
    return ok(message="Item do orçamento removido.", data=None, request=request)
