from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.cliente_contato import ClienteContato
from app.models.orcamento import Orcamento
from app.models.contrato import Contrato
from app.schemas.cliente import ClienteCreate, ClienteUpdate


def _raise_cnpj_unique_error() -> None:
    """Mensagem amigável quando violar unique do CNPJ."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Já existe um cliente cadastrado com este CNPJ.",
    )


async def _has_vinculos_criticos(db: AsyncSession, cliente_id: int) -> bool:
    """
    Retorna True se existir vínculo que impeça desativar o cliente.
    - Orcamentos (cliente_id)
    - Contratos (cliente_id)
    """
    # Orcamentos vinculados?
    q_orc = await db.execute(
        select(func.count(Orcamento.id)).where(Orcamento.cliente_id == cliente_id)
    )
    if (q_orc.scalar() or 0) > 0:
        return True

    # Contratos vinculados?
    q_con = await db.execute(
        select(func.count(Contrato.id)).where(Contrato.cliente_id == cliente_id)
    )
    if (q_con.scalar() or 0) > 0:
        return True

    return False


async def create(db: AsyncSession, data: ClienteCreate) -> Cliente:
    """
    Cria cliente e opcionalmente já cria seus contatos (1 request).
    Usa transação e trata conflito de CNPJ unique.
    """
    payload = data.model_dump(exclude={"contatos"})
    obj = Cliente(**payload)

    # Contatos (nested create)
    for c in data.contatos:
        contato = ClienteContato(**c.model_dump())
        obj.contatos.append(contato)

    db.add(obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # Provável violação do unique do CNPJ
        _raise_cnpj_unique_error()

    await db.refresh(obj)
    return obj


async def get(db: AsyncSession, cliente_id: int) -> Optional[Cliente]:
    return await db.get(Cliente, cliente_id)


async def list_(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    nome: str | None = None,
    cnpj: str | None = None,
    ativo: bool | None = None,
) -> list[Cliente]:
    """
    Lista clientes com filtros básicos.
    - nome: contém (case-insensitive)
    - cnpj: exato (pode ajustar para contains no futuro)
    - ativo: True/False
    """
    stmt = select(Cliente).order_by(Cliente.id).offset(skip).limit(limit)

    conds = []
    if nome:
        conds.append(Cliente.nome.ilike(f"%{nome}%"))
    if cnpj:
        conds.append(Cliente.cnpj == cnpj)
    if ativo is not None:
        conds.append(Cliente.ativo == ativo)

    if conds:
        stmt = stmt.where(and_(*conds)).order_by(Cliente.id).offset(skip).limit(limit)

    res = await db.execute(stmt)
    return list(res.scalars())


async def update(db: AsyncSession, cliente_id: int, data: ClienteUpdate) -> Optional[Cliente]:
    """
    Atualiza dados do cliente (parcial).
    Contatos são tratados via sub-recurso (repo cliente_contato).
    """
    obj = await db.get(Cliente, cliente_id)
    if not obj:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        _raise_cnpj_unique_error()

    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, cliente_id: int) -> bool:
    """
    Soft delete: desativa o cliente (ativo=false).
    Protege se houver vínculos críticos (orçamentos/contratos).
    """
    obj = await db.get(Cliente, cliente_id)
    if not obj:
        return False

    # Se já está inativo, consideramos ok (idempotente)
    if obj.ativo is False:
        return True

    if await _has_vinculos_criticos(db, cliente_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível desativar o cliente pois existem vínculos (orçamentos e/ou contratos).",
        )

    obj.ativo = False
    await db.commit()
    return True