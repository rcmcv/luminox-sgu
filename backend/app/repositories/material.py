from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate

async def create(db: AsyncSession, data: MaterialCreate) -> Material:
    obj = Material(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, material_id: int) -> Optional[Material]:
    return await db.get(Material, material_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Material]:
    res = await db.execute(select(Material).order_by(Material.nome).offset(skip).limit(limit))
    return list(res.scalars())

async def update(db: AsyncSession, material_id: int, data: MaterialUpdate) -> Optional[Material]:
    obj = await db.get(Material, material_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, material_id: int) -> bool:
    obj = await db.get(Material, material_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
