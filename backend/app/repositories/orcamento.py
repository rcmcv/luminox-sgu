from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.orcamento import Orcamento
from app.models.cliente import Cliente
from app.models.contrato import Contrato

def _validate_tipo_contrato(tipo: str, contrato_id: int | None):
    if tipo == "CONTRATO" and not contrato_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Para tipo CONTRATO é obrigatório informar contrato_id."
        )
    if tipo == "SPOT" and contrato_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Para tipo SPOT o contrato_id deve ser nulo."
        )

async def _ensure_cliente_exists(db: AsyncSession, cliente_id: int) -> None:
    if not await db.get(Cliente, cliente_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cliente informado não existe."
        )

async def _ensure_contrato_belongs_to_cliente(db: AsyncSession, contrato_id: int, cliente_id: int) -> None:
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contrato informado não existe."
        )
    if contrato.cliente_id != cliente_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contrato informado não pertence ao cliente."
        )

async def create(db: AsyncSession, data) -> Orcamento:
    _validate_tipo_contrato(data.tipo, data.contrato_id)
    # NOVO: cliente deve existir sempre
    await _ensure_cliente_exists(db, data.cliente_id)
    # NOVO: se for CONTRATO, precisa pertencer ao cliente
    if data.tipo == "CONTRATO":
        await _ensure_contrato_belongs_to_cliente(db, data.contrato_id, data.cliente_id)  # type: ignore[arg-type]
    obj = Orcamento(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def update(db: AsyncSession, orcamento_id: int, data) -> Optional[Orcamento]:
    obj = await db.get(Orcamento, orcamento_id)
    if not obj:
        return None

    incoming = data.model_dump(exclude_unset=True)
    tipo = incoming.get("tipo", obj.tipo)
    contrato_id = incoming.get("contrato_id", obj.contrato_id)
    cliente_id = incoming.get("cliente_id", obj.cliente_id)

    _validate_tipo_contrato(tipo, contrato_id)

    # NOVO: cliente precisa existir (se mudar ou mesmo se mantiver)
    await _ensure_cliente_exists(db, cliente_id)

    # NOVO: se for CONTRATO, garante vínculo contrato-cliente
    if tipo == "CONTRATO":
        if contrato_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Para tipo CONTRATO é obrigatório informar contrato_id."
            )
        await _ensure_contrato_belongs_to_cliente(db, contrato_id, cliente_id)

    for k, v in incoming.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

async def get(db: AsyncSession, orcamento_id: int) -> Optional[Orcamento]:
    return await db.get(Orcamento, orcamento_id)

async def list_(db: AsyncSession, skip: int = 0, limit: int = 50, cliente_id: int | None = None, tipo: str | None = None) -> List[Orcamento]:
    stmt = select(Orcamento).order_by(Orcamento.id).offset(skip).limit(limit)
    if cliente_id or tipo:
        from sqlalchemy import and_
        conds = []
        if cliente_id:
            conds.append(Orcamento.cliente_id == cliente_id)
        if tipo:
            conds.append(Orcamento.tipo == tipo)
        stmt = select(Orcamento).where(and_(*conds)).order_by(Orcamento.id).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars())

async def delete(db: AsyncSession, orcamento_id: int) -> bool:
    obj = await db.get(Orcamento, orcamento_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True
