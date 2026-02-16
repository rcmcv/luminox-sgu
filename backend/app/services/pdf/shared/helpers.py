from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable


def normalize_name(value: str) -> str:
    value = (value or "").strip().lower()
    return (
        value.replace("á", "a").replace("ã", "a").replace("â", "a")
        .replace("é", "e").replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o").replace("ô", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def escape(text: Any) -> str:
    s = str(text) if text is not None else ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_date(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, (datetime, date)):
        return v.strftime("%d/%m/%Y")
    try:
        s = str(v)
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            yyyy, mm_, dd = s[:10].split("-")
            return f"{dd}/{mm_}/{yyyy}"
        return s
    except Exception:
        return "-"


def fmt_number(v: Any) -> str:
    try:
        n = float(v)
        if abs(n - int(n)) < 1e-9:
            return str(int(n))
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0"


def fmt_money(v: Any) -> str:
    if v is None:
        return "R$ 0,00"
    try:
        n = float(v)
        s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {s}"
    except Exception:
        return "R$ 0,00"


def fmt_money_no_prefix(v: Any) -> str:
    if v is None:
        return "0,00"
    try:
        n = float(v)
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def to_float(v: Any) -> float:
    try:
        if v is None:
            return 0.0
        return float(v)
    except Exception:
        return 0.0


def sum_totais_itens(itens: Iterable[Any]) -> float:
    total = 0.0
    for item in itens:
        t = getattr(item, "total", None)
        if t is None:
            qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
            unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or 0
            t = to_float(qtd) * to_float(unit)
        total += to_float(t)
    return total
