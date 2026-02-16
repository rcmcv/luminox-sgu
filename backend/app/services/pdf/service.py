from __future__ import annotations

from typing import Any, Iterable

from .shared.constants import (
    LAYOUT_PADRAO,
    LAYOUT_ULTRAGAZ,
    LAYOUT_ACO_CEARENSE,
    CLIENTE_ULTRAGAZ,
    CLIENTE_ACO_CEARENSE,
)
from .shared.helpers import normalize_name
from .layouts.padrao import render_pdf_padrao
from .layouts.ultragaz import render_pdf_ultragaz
from .layouts.aco_cearense import render_pdf_aco_cearense


def escolher_layout_cliente(cliente: Any) -> str:
    """
    Decide qual layout usar com base no cliente.
    """
    nome = getattr(cliente, "nome", None) or getattr(cliente, "name", "") or ""
    nome_norm = normalize_name(str(nome))

    if nome_norm == CLIENTE_ACO_CEARENSE:
        return LAYOUT_ACO_CEARENSE

    if nome_norm == CLIENTE_ULTRAGAZ:
        return LAYOUT_ULTRAGAZ

    return LAYOUT_PADRAO


def generate_orcamento_pdf(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Função pública usada pelos endpoints. Retorna os bytes do PDF.
    """
    layout = escolher_layout_cliente(cliente)

    if layout == LAYOUT_PADRAO:
        return render_pdf_padrao(orcamento, itens, cliente)

    if layout == LAYOUT_ULTRAGAZ:
        return render_pdf_ultragaz(orcamento, itens, cliente)

    if layout == LAYOUT_ACO_CEARENSE:
        # ainda não implementado (mantém a regra atual)
        return render_pdf_aco_cearense(orcamento, itens, cliente)

    raise NotImplementedError("Layout de PDF não suportado.")
