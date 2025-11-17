from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tipo_servico import TipoServico
from app.schemas.tipo_servico import TipoServicoCreate, TipoServicoUpdate

async def create(db: AsyncSession, data: TipoServicoCreate) -> TipoServico:
    obj = TipoServico(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, tipo_id: int) -> Optional[TipoServico]:
    return await db.get(TipoServico, tipo_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[TipoServico]:
    res = await db.execute(select(TipoServico).order_by(TipoServico.nome).offset(skip).limit(limit))
    return list(res.scalars())

async def update(db: AsyncSession, tipo_id: int, data: TipoServicoUpdate) -> Optional[TipoServico]:
    obj = await db.get(TipoServico, tipo_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, tipo_id: int) -> bool:
    obj = await db.get(TipoServico, tipo_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
