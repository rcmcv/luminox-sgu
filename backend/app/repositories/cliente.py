from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

async def create(db: AsyncSession, data: ClienteCreate) -> Cliente:
    obj = Cliente(nome=data.nome, email=data.email, telefone=data.telefone)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, cliente_id: int) -> Optional[Cliente]:
    return await db.get(Cliente, cliente_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Cliente]:
    res = await db.execute(select(Cliente).offset(skip).limit(limit))
    return list(res.scalars())

async def update(db: AsyncSession, cliente_id: int, data: ClienteUpdate) -> Optional[Cliente]:
    obj = await db.get(Cliente, cliente_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, cliente_id: int) -> bool:
    obj = await db.get(Cliente, cliente_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
