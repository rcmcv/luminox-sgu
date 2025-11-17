# app/services/precos_contrato.py
from typing import Literal, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.contrato import Contrato
from app.models.contrato_hh_preco import ContratoHHPreco, TIPOS_HH
from app.models.contrato_material_preco import ContratoMaterialPreco

TipoHH = Literal["REGULAR", "EXTRA", "FERIADO"]

async def _get_contrato_or_404(db: AsyncSession, contrato_id: int) -> Contrato:
    contrato = await db.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")
    return contrato

async def resolve_preco_hh(
    db: AsyncSession,
    contrato_id: int,
    maquina_id: int,
    tipo_hh: TipoHH,
) -> dict:
    """
    1) Tenta preço específico (contrato_id + maquina_id + tipo_hh)
    2) Se não existir, usa o default do contrato conforme tipo_hh
    3) Retorna dict informando 'fonte': 'especifico' | 'default'
    """
    if tipo_hh not in TIPOS_HH:
        raise HTTPException(status_code=400, detail=f"tipo_hh inválido. Use um de {TIPOS_HH}.")

    contrato = await _get_contrato_or_404(db, contrato_id)

    # Preço específico?
    stmt = (
        select(ContratoHHPreco)
        .where(
            (ContratoHHPreco.contrato_id == contrato_id)
            & (ContratoHHPreco.maquina_id == maquina_id)
            & (ContratoHHPreco.tipo_hh == tipo_hh)
        )
        .limit(1)
    )
    res = await db.execute(stmt)
    esp: Optional[ContratoHHPreco] = res.scalars().first()

    if esp:
        return {
            "preco": float(esp.preco_hora),
            "fonte": "especifico",
            "uom_id": esp.uom_id,
            "contrato_id": contrato_id,
            "maquina_id": maquina_id,
            "tipo_hh": tipo_hh,
        }

    # Fallback: default do contrato
    default_map = {
        "REGULAR": contrato.hh_regular_default,
        "EXTRA": contrato.hh_extra_default,
        "FERIADO": contrato.hh_feriado_default,
    }
    valor_default = default_map.get(tipo_hh)

    if valor_default is None:
        # sem específico e sem default → regra de negócio: 422
        raise HTTPException(
            status_code=422,
            detail="Preço de HH não configurado (nem específico, nem default)."
        )

    return {
        "preco": float(valor_default),
        "fonte": "default",
        "uom_id": None,  # default não tem UoM específico aqui
        "contrato_id": contrato_id,
        "maquina_id": maquina_id,
        "tipo_hh": tipo_hh,
    }

async def resolve_preco_material(
    db: AsyncSession,
    contrato_id: int,
    material_id: int,
) -> dict:
    """
    1) Tenta preço específico (contrato_id + material_id)
    2) Se não existir, usa material_kg_default do contrato
       (assumindo que a UoM de referência do default é 'kg' – simples por enquanto)
    """
    contrato = await _get_contrato_or_404(db, contrato_id)

    stmt = (
        select(ContratoMaterialPreco)
        .where(
            (ContratoMaterialPreco.contrato_id == contrato_id)
            & (ContratoMaterialPreco.material_id == material_id)
        )
        .limit(1)
    )
    res = await db.execute(stmt)
    esp: Optional[ContratoMaterialPreco] = res.scalars().first()

    if esp:
        return {
            "preco": float(esp.preco_unitario),
            "fonte": "especifico",
            "uom_id": esp.uom_id,
            "contrato_id": contrato_id,
            "material_id": material_id,
        }

    if contrato.material_kg_default is None:
        raise HTTPException(
            status_code=422,
            detail="Preço de material não configurado (nem específico, nem default por kg)."
        )

    return {
        "preco": float(contrato.material_kg_default),
        "fonte": "default",
        "uom_id": None,  # default simples (por kg) – refinamos depois se precisar
        "contrato_id": contrato_id,
        "material_id": material_id,
    }
