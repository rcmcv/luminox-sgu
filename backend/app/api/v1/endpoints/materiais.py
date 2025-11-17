from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user, require_roles
from app.deps.pagination import get_pagination
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
from app.repositories import material as repo
from app.core.api import ok, created

router = APIRouter()

@router.post(
    "/materiais",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def create_material(payload: MaterialCreate, request: Request, db: AsyncSession = Depends(get_db)):
    obj = await repo.create(db, payload)
    data = {
        "id": obj.id, "nome": obj.nome, "descricao": obj.descricao, "uom_base_id": obj.uom_base_id,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return created(data=data, message="Material criado com sucesso.", request=request)

@router.get("/materiais", response_model=None)
async def list_materiais(request: Request, pagination = Depends(get_pagination), db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    items = await repo.list_(db, skip=pagination.skip, limit=pagination.limit)
    meta = {"page": pagination.page, "size": pagination.size, "count": len(items)}
    data = [
        {
            "id": i.id, "nome": i.nome, "descricao": i.descricao, "uom_base_id": i.uom_base_id,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        } for i in items
    ]
    return ok(data=data, meta=meta, request=request)

@router.get("/materiais/{material_id}", response_model=MaterialOut)
async def get_material(material_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    obj = await repo.get(db, material_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return obj

@router.put(
    "/materiais/{material_id}",
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def update_material(material_id: int, payload: MaterialUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    obj = await repo.update(db, material_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    data = {
        "id": obj.id, "nome": obj.nome, "descricao": obj.descricao, "uom_base_id": obj.uom_base_id,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
        "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
    }
    return ok(data=data, message="Material atualizado com sucesso.", request=request)

@router.delete(
    "/materiais/{material_id}",
    status_code=status.HTTP_200_OK,
    response_model=None,
    dependencies=[Depends(require_roles("ADMIN", "OPERACAO"))],
)
async def delete_material(material_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    removed = await repo.delete(db, material_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return ok(message="Material removido com sucesso.", data=None, request=request)
