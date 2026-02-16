from __future__ import annotations

from dataclasses import dataclass
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


@dataclass(frozen=True)
class PdfPageFormat:
    page_size = A4
    left_margin = 8 * mm
    right_margin = 8 * mm
    top_margin = 8 * mm
    bottom_margin = 8 * mm
