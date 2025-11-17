from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.fornecedor import Fornecedor
from app.schemas.fornecedor import FornecedorCreate, FornecedorUpdate

async def create(db: AsyncSession, data: FornecedorCreate) -> Fornecedor:
    obj = Fornecedor(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, fornecedor_id: int) -> Optional[Fornecedor]:
    return await db.get(Fornecedor, fornecedor_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Fornecedor]:
    res = await db.execute(select(Fornecedor).order_by(Fornecedor.id).offset(skip).limit(limit))
    return list(res.scalars())

async def update(db: AsyncSession, fornecedor_id: int, data: FornecedorUpdate) -> Optional[Fornecedor]:
    obj = await db.get(Fornecedor, fornecedor_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, fornecedor_id: int) -> bool:
    obj = await db.get(Fornecedor, fornecedor_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
