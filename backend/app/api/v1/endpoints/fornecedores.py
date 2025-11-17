from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate, FornecedorOut
from app.repositories import fornecedor as repo
from app.core.api import ok, created
from app.deps.pagination import get_pagination

router = APIRouter()

@router.post(
    "/fornecedores",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_fornecedor(
    payload: FornecedorCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id,
        "nome": obj.nome,
        "cnpj": obj.cnpj,
        "email": obj.email,
        "telefone": obj.telefone,
        "contato": obj.contato,
        "observacoes": obj.observacoes,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Fornecedor criado com sucesso.", request=request)

@router.get("/fornecedores", response_model=None)
async def list_fornecedores(
    request: Request,
    pagination = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id,
            "nome": i.nome,
            "cnpj": i.cnpj,
            "email": i.email,
            "telefone": i.telefone,
            "contato": i.contato,
            "observacoes": i.observacoes,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        }
        for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/fornecedores/{fornecedor_id}", response_model=FornecedorOut)
async def get_fornecedor(
    fornecedor_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
):
    obj = await repo.get(db, fornecedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return obj

@router.put(
    "/fornecedores/{fornecedor_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_fornecedor(
    fornecedor_id: int,
    payload: FornecedorUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    obj = await repo.update(db, fornecedor_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    data = {
        "id": obj.id,
        "nome": obj.nome,
        "cnpj": obj.cnpj,
        "email": obj.email,
        "telefone": obj.telefone,
        "contato": obj.contato,
        "observacoes": obj.observacoes,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Fornecedor atualizado com sucesso.", request=request)

@router.delete(
    "/fornecedores/{fornecedor_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_fornecedor(
    fornecedor_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ok_del = await repo.delete(db, fornecedor_id)
    if not ok_del:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return ok(message="Fornecedor removido com sucesso.", data=None, request=request)
