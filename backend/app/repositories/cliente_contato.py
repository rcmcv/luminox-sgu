from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.cliente_contato import ClienteContato
from app.schemas.cliente_contato import ClienteContatoCreate, ClienteContatoUpdate


async def _ensure_cliente_exists(db: AsyncSession, cliente_id: int) -> None:
    if not await db.get(Cliente, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")


async def _get_contato(db: AsyncSession, cliente_id: int, contato_id: int) -> Optional[ClienteContato]:
    """
    Carrega o contato garantindo que pertence ao cliente.
    """
    stmt = select(ClienteContato).where(
        and_(
            ClienteContato.id == contato_id,
            ClienteContato.cliente_id == cliente_id,
        )
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def list_(
    db: AsyncSession,
    cliente_id: int,
    ativo: bool | None = True,
) -> list[ClienteContato]:
    """
    Lista contatos do cliente.
    Por padrão retorna apenas ativos (ativo=True).
    Se ativo=None, retorna todos.
    """
    await _ensure_cliente_exists(db, cliente_id)

    stmt = select(ClienteContato).where(ClienteContato.cliente_id == cliente_id).order_by(ClienteContato.id)

    if ativo is not None:
        stmt = stmt.where(ClienteContato.ativo == ativo)

    res = await db.execute(stmt)
    return list(res.scalars())


async def create(db: AsyncSession, cliente_id: int, data: ClienteContatoCreate) -> ClienteContato:
    await _ensure_cliente_exists(db, cliente_id)

    obj = ClienteContato(cliente_id=cliente_id, **data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(
    db: AsyncSession,
    cliente_id: int,
    contato_id: int,
    data: ClienteContatoUpdate,
) -> Optional[ClienteContato]:
    obj = await _get_contato(db, cliente_id, contato_id)
    if not obj:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, cliente_id: int, contato_id: int) -> bool:
    """
    Soft delete do contato: ativo=false.
    """
    obj = await _get_contato(db, cliente_id, contato_id)
    if not obj:
        return False

    if obj.ativo is False:
        return True

    obj.ativo = False
    await db.commit()
    return True