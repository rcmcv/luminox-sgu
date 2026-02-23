from __future__ import annotations

from dataclasses import dataclass
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


@dataclass(frozen=True)
class PdfPageFormat:
    """
    Formato/base para criação do PDF (tamanho + margens).
    Centralizamos isso aqui para evitar duplicação e inconsistências entre layouts.
    """
    page_size = A4
    left_margin: float = 8 * mm
    right_margin: float = 8 * mm
    top_margin: float = 8 * mm
    bottom_margin: float = 8 * mm


# Presets (deixam explícito quando um layout usa margens diferentes)
PDF_FORMAT_PADRAO = PdfPageFormat(
    left_margin=8 * mm,
    right_margin=8 * mm,
    top_margin=8 * mm,
    bottom_margin=8 * mm,
)

PDF_FORMAT_ULTRAGAZ = PdfPageFormat(
    left_margin=12 * mm,
    right_margin=12 * mm,
    top_margin=10 * mm,
    bottom_margin=12 * mm,
)

PDF_FORMAT_ACO_CEARENSE = PdfPageFormat(
    left_margin=16 * mm,
    right_margin=16 * mm,
    top_margin=16 * mm,
    bottom_margin=16 * mm,
)
