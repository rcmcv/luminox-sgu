from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user  # VIEWER pode ler
from app.core.api import ok
from app.services.precos_contrato import resolve_preco_hh, resolve_preco_material

router = APIRouter()

@router.get("/contratos/{contrato_id}/precos/hh", response_model=None)
async def preview_preco_hh(
    contrato_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    maquina_id: int = Query(..., ge=1),
    tipo_hh: str = Query(..., pattern="^(REGULAR|EXTRA|FERIADO)$"),
):
    resolved = await resolve_preco_hh(db, contrato_id=contrato_id, maquina_id=maquina_id, tipo_hh=tipo_hh)  # type: ignore
    return ok(data=resolved, message="Preço de HH resolvido.", request=request)

@router.get("/contratos/{contrato_id}/precos/material", response_model=None)
async def preview_preco_material(
    contrato_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    material_id: int = Query(..., ge=1),
):
    resolved = await resolve_preco_material(db, contrato_id=contrato_id, material_id=material_id)
    return ok(data=resolved, message="Preço de material resolvido.", request=request)
