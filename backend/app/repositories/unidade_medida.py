from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.unidade_medida import UnidadeMedida
from app.schemas.unidade_medida import UoMCreate, UoMUpdate

async def create(db: AsyncSession, data: UoMCreate) -> UnidadeMedida:
    obj = UnidadeMedida(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, uom_id: int) -> Optional[UnidadeMedida]:
    return await db.get(UnidadeMedida, uom_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[UnidadeMedida]:
    res = await db.execute(
        select(UnidadeMedida).order_by(UnidadeMedida.nome).offset(skip).limit(limit)
    )
    return list(res.scalars())

async def update(db: AsyncSession, uom_id: int, data: UoMUpdate) -> Optional[UnidadeMedida]:
    obj = await db.get(UnidadeMedida, uom_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, uom_id: int) -> bool:
    obj = await db.get(UnidadeMedida, uom_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
