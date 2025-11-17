from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.core.api import ok, created
from app.schemas.orcamento import OrcamentoCreate, OrcamentoUpdate, OrcamentoOut
from app.repositories import orcamento as repo

router = APIRouter()

@router.post(
    "/orcamentos",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_orcamento(
    payload: OrcamentoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    return created(
        data={
            "id": obj.id,
            "cliente_id": obj.cliente_id,
            "tipo": obj.tipo,
            "status": obj.status,
            "contrato_id": obj.contrato_id,
            "moeda": obj.moeda,
            "titulo": obj.titulo,
            "observacoes": obj.observacoes,
            "subtotal": float(obj.subtotal),
            "desconto": float(obj.desconto),
            "acrescimo": float(obj.acrescimo),
            "total": float(obj.total),
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        },
        message="Orçamento criado com sucesso.",
        request=request,
    )

@router.get("/orcamentos", response_model=None)
async def list_orcamentos(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),  # VIEWER pode listar
    cliente_id: int | None = Query(None, ge=1),
    tipo: str | None = Query(None),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit, cliente_id=cliente_id, tipo=tipo)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "cliente_id": i.cliente_id,
            "tipo": i.tipo,
            "status": i.status,
            "contrato_id": i.contrato_id,
            "moeda": i.moeda,
            "titulo": i.titulo,
            "observacoes": i.observacoes,
            "subtotal": float(i.subtotal),
            "desconto": float(i.desconto),
            "acrescimo": float(i.acrescimo),
            "total": float(i.total),
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/orcamentos/{orcamento_id}", response_model=OrcamentoOut)
async def get_orcamento(
    orcamento_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, orcamento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return obj

@router.put(
    "/orcamentos/{orcamento_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_orcamento(
    orcamento_id: int,
    payload: OrcamentoUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, orcamento_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return ok(
        data={
            "id": obj.id,
            "cliente_id": obj.cliente_id,
            "tipo": obj.tipo,
            "status": obj.status,
            "contrato_id": obj.contrato_id,
            "moeda": obj.moeda,
            "titulo": obj.titulo,
            "observacoes": obj.observacoes,
            "subtotal": float(obj.subtotal),
            "desconto": float(obj.desconto),
            "acrescimo": float(obj.acrescimo),
            "total": float(obj.total),
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        },
        message="Orçamento atualizado com sucesso.",
        request=request,
    )

@router.delete(
    "/orcamentos/{orcamento_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_orcamento(
    orcamento_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    removed = await repo.delete(db, orcamento_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    return ok(message="Orçamento removido com sucesso.", data=None, request=request)
