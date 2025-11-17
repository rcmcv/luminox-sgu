from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.orcamento import Orcamento
from app.models.orcamento_item import OrcamentoItem
from app.schemas.orcamento_item import OrcamentoItemCreate, OrcamentoItemUpdate
from app.services.precos_contrato import resolve_preco_hh, resolve_preco_material

# ------ Helpers de regra de negócio ------

def _require(cond: bool, msg: str):
    if not cond:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)

async def _recalcular_totais(db: AsyncSession, orcamento_id: int) -> None:
    stmt = select(func.coalesce(func.sum(OrcamentoItem.total_item), 0)).where(OrcamentoItem.orcamento_id == orcamento_id)
    total_itens = (await db.execute(stmt)).scalar_one()
    orc = await db.get(Orcamento, orcamento_id)
    if not orc:
        return
    orc.subtotal = float(total_itens)
    orc.total = float(orc.subtotal) - float(orc.desconto or 0) + float(orc.acrescimo or 0)
    await db.commit()
    await db.refresh(orc)

async def _resolver_preco_para_item(
    db: AsyncSession, orc: Orcamento, data: OrcamentoItemCreate | OrcamentoItemUpdate
) -> tuple[float, int | None]:
    """
    Retorna (preco_unitario, uom_id_resolvido)
    - CONTRATO + HH  -> resolve via contrato_hh_preco
    - CONTRATO + MATERIAL -> resolve via contrato_material_preco
    - SPOT + LIVRE -> usa preco_unitario enviado
    - SPOT + HH/MATERIAL -> permitido também enviar preco_unitario manual (flexível)
    """
    # valores atuais / incoming
    item_tipo = getattr(data, "item_tipo", None)
    if item_tipo is None:
        # em update, manter o existente; no create, schema obriga item_tipo
        pass

    if item_tipo == "HH":
        _require(getattr(data, "maquina_id", None), "maquina_id é obrigatório para item HH.")
        _require(getattr(data, "tipo_hh", None), "tipo_hh é obrigatório para item HH.")
        if orc.tipo == "CONTRATO":
            resolved = await resolve_preco_hh(
                db, contrato_id=orc.contrato_id,  # type: ignore[arg-type]
                maquina_id=data.maquina_id, tipo_hh=data.tipo_hh  # type: ignore[arg-type]
            )
            return resolved["preco"], resolved.get("uom_id")
        else:
            # SPOT -> aceita preco_unitario manual
            pu = getattr(data, "preco_unitario", None)
            _require(pu is not None, "preco_unitario é obrigatório para item HH em orçamento SPOT.")
            return float(pu), getattr(data, "uom_id", None)

    if item_tipo == "MATERIAL":
        _require(getattr(data, "material_id", None), "material_id é obrigatório para item MATERIAL.")
        if orc.tipo == "CONTRATO":
            resolved = await resolve_preco_material(
                db, contrato_id=orc.contrato_id,  # type: ignore[arg-type]
                material_id=data.material_id  # type: ignore[arg-type]
            )
            return resolved["preco"], resolved.get("uom_id")
        else:
            pu = getattr(data, "preco_unitario", None)
            _require(pu is not None, "preco_unitario é obrigatório para item MATERIAL em orçamento SPOT.")
            return float(pu), getattr(data, "uom_id", None)

    if item_tipo == "LIVRE":
        _require(getattr(data, "descricao", None), "descricao é obrigatória para item LIVRE.")
        pu = getattr(data, "preco_unitario", None)
        _require(pu is not None, "preco_unitario é obrigatório para item LIVRE.")
        return float(pu), getattr(data, "uom_id", None)

    raise HTTPException(status_code=422, detail="item_tipo inválido. Use HH, MATERIAL ou LIVRE.")

# ------ CRUD ------

async def create(db: AsyncSession, orcamento_id: int, data: OrcamentoItemCreate) -> OrcamentoItem:
    orc = await db.get(Orcamento, orcamento_id)
    if not orc:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    preco_unit, uom_res = await _resolver_preco_para_item(db, orc, data)
    qtd = float(data.quantidade or 1)
    total_item = round(qtd * float(preco_unit), 2)

    obj = OrcamentoItem(
        orcamento_id=orcamento_id,
        item_tipo=data.item_tipo,
        maquina_id=data.maquina_id,
        tipo_hh=data.tipo_hh,
        material_id=data.material_id,
        descricao=data.descricao,
        uom_id=(uom_res or data.uom_id),
        quantidade=qtd,
        preco_unitario=preco_unit,
        total_item=total_item,
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    await _recalcular_totais(db, orcamento_id)
    return obj

async def get(db: AsyncSession, item_id: int) -> Optional[OrcamentoItem]:
    return await db.get(OrcamentoItem, item_id)

async def list_(db: AsyncSession, orcamento_id: int) -> List[OrcamentoItem]:
    stmt = select(OrcamentoItem).where(OrcamentoItem.orcamento_id == orcamento_id).order_by(OrcamentoItem.id)
    res = await db.execute(stmt)
    return list(res.scalars())

async def update(db: AsyncSession, orcamento_id: int, item_id: int, data: OrcamentoItemUpdate) -> Optional[OrcamentoItem]:
    obj = await db.get(OrcamentoItem, item_id)
    if not obj or obj.orcamento_id != orcamento_id:
        return None

    orc = await db.get(Orcamento, orcamento_id)
    if not orc:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    # aplica campos
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    # resolver preço se necessário
    preco_unit, uom_res = await _resolver_preco_para_item(db, orc, data if data.item_tipo else obj)
    obj.preco_unitario = preco_unit
    if uom_res:
        obj.uom_id = uom_res

    qtd = float(obj.quantidade or 1)
    obj.total_item = round(qtd * float(obj.preco_unitario), 2)

    await db.commit()
    await db.refresh(obj)
    await _recalcular_totais(db, orcamento_id)
    return obj

async def delete(db: AsyncSession, orcamento_id: int, item_id: int) -> bool:
    obj = await db.get(OrcamentoItem, item_id)
    if not obj or obj.orcamento_id != orcamento_id:
        return False
    await db.delete(obj)
    await db.commit()
    await _recalcular_totais(db, orcamento_id)
    return True
