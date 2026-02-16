from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image


def get_app_dir() -> Path:
    """
    Retorna o diretório /backend/app a partir deste arquivo:
    backend/app/services/pdf/shared/assets.py
    """
    return Path(__file__).resolve().parents[3]


def get_logo_path() -> Path:
    """
    Caminho padronizado da logo dentro do backend.
    """
    return get_app_dir() / "assets" / "logo" / "logo_luminox_preta.png"


def build_logo_image(width_mm: float = 65.0) -> Optional[Image]:
    """
    Cria um Image (ReportLab) com largura em mm e altura proporcional.
    Retorna None se o arquivo não existir.

    - width_mm: largura desejada (ex.: 65mm para "logo grande, bem forte")
    """
    logo_path = get_logo_path()
    if not logo_path.exists():
        return None

    # Descobre dimensões reais (px) para manter proporção
    ir = ImageReader(str(logo_path))
    px_w, px_h = ir.getSize()

    # Converte largura para points (via mm) e calcula altura proporcional
    w = width_mm * mm
    h = w * (px_h / float(px_w))

    img = Image(str(logo_path), width=w, height=h)
    img.hAlign = "LEFT"
    return img
