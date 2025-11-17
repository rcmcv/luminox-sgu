from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.maquina import Maquina
from app.schemas.maquina import MaquinaCreate, MaquinaUpdate

async def create(db: AsyncSession, data: MaquinaCreate) -> Maquina:
    obj = Maquina(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, maquina_id: int) -> Optional[Maquina]:
    return await db.get(Maquina, maquina_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Maquina]:
    res = await db.execute(select(Maquina).order_by(Maquina.nome).offset(skip).limit(limit))
    return list(res.scalars())

async def update(db: AsyncSession, maquina_id: int, data: MaquinaUpdate) -> Optional[Maquina]:
    obj = await db.get(Maquina, maquina_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, maquina_id: int) -> bool:
    obj = await db.get(Maquina, maquina_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
