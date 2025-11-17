from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.contrato import Contrato
from app.schemas.contrato import ContratoCreate, ContratoUpdate

async def create(db: AsyncSession, data: ContratoCreate) -> Contrato:
    obj = Contrato(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, contrato_id: int) -> Optional[Contrato]:
    return await db.get(Contrato, contrato_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50, cliente_id: int | None = None) -> List[Contrato]:
    stmt = select(Contrato).order_by(Contrato.id).offset(skip).limit(limit)
    if cliente_id:
        stmt = select(Contrato).where(Contrato.cliente_id == cliente_id).order_by(Contrato.id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars())

async def update(db: AsyncSession, contrato_id: int, data: ContratoUpdate) -> Optional[Contrato]:
    obj = await db.get(Contrato, contrato_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, contrato_id: int) -> bool:
    obj = await db.get(Contrato, contrato_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
