from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.contrato_material_preco import ContratoMaterialPreco
from app.schemas.contrato_material_preco import (
    ContratoMaterialPrecoCreate, ContratoMaterialPrecoUpdate
)

async def create(db: AsyncSession, data: ContratoMaterialPrecoCreate) -> ContratoMaterialPreco:
    obj = ContratoMaterialPreco(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, preco_id: int) -> Optional[ContratoMaterialPreco]:
    return await db.get(ContratoMaterialPreco, preco_id)

async def list_(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    contrato_id: int | None = None,
    material_id: int | None = None,
) -> List[ContratoMaterialPreco]:
    stmt = select(ContratoMaterialPreco).order_by(ContratoMaterialPreco.id).offset(skip).limit(limit)
    if contrato_id or material_id:
        conds = []
        if contrato_id:
            conds.append(ContratoMaterialPreco.contrato_id == contrato_id)
        if material_id:
            conds.append(ContratoMaterialPreco.material_id == material_id)
        stmt = select(ContratoMaterialPreco).where(and_(*conds)).order_by(ContratoMaterialPreco.id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars())

async def update(db: AsyncSession, preco_id: int, data: ContratoMaterialPrecoUpdate) -> Optional[ContratoMaterialPreco]:
    obj = await db.get(ContratoMaterialPreco, preco_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, preco_id: int) -> bool:
    obj = await db.get(ContratoMaterialPreco, preco_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
