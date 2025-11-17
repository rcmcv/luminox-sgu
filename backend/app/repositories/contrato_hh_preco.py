from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.contrato_hh_preco import ContratoHHPreco
from app.schemas.contrato_hh_preco import ContratoHHPrecoCreate, ContratoHHPrecoUpdate

async def create(db: AsyncSession, data: ContratoHHPrecoCreate) -> ContratoHHPreco:
    obj = ContratoHHPreco(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, preco_id: int) -> Optional[ContratoHHPreco]:
    return await db.get(ContratoHHPreco, preco_id)

async def list_(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    contrato_id: int | None = None,
    maquina_id: int | None = None,
    tipo_hh: str | None = None,
) -> List[ContratoHHPreco]:
    stmt = select(ContratoHHPreco).order_by(ContratoHHPreco.id).offset(skip).limit(limit)
    if contrato_id or maquina_id or tipo_hh:
        conds = []
        if contrato_id:
            conds.append(ContratoHHPreco.contrato_id == contrato_id)
        if maquina_id:
            conds.append(ContratoHHPreco.maquina_id == maquina_id)
        if tipo_hh:
            conds.append(ContratoHHPreco.tipo_hh == tipo_hh)
        stmt = select(ContratoHHPreco).where(and_(*conds)).order_by(ContratoHHPreco.id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars())

async def update(db: AsyncSession, preco_id: int, data: ContratoHHPrecoUpdate) -> Optional[ContratoHHPreco]:
    obj = await db.get(ContratoHHPreco, preco_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, preco_id: int) -> bool:
    obj = await db.get(ContratoHHPreco, preco_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
