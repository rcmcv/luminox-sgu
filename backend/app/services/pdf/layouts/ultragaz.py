from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from io import BytesIO
from typing import Any, Iterable

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


@dataclass(frozen=True)
class PdfOrcamentoFormat:
    page_size = A4
    left_margin = 12 * mm
    right_margin = 12 * mm
    top_margin = 10 * mm
    bottom_margin = 12 * mm


def render_pdf_ultragaz(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout ULTRAGAZ (conforme LAYOUT_ULTRAGAZ.pdf).
    """
    buf = BytesIO()
    fmt = PdfOrcamentoFormat()

    doc = SimpleDocTemplate(
        buf,
        pagesize=fmt.page_size,
        leftMargin=fmt.left_margin,
        rightMargin=fmt.right_margin,
        topMargin=fmt.top_margin,
        bottomMargin=fmt.bottom_margin,
        title="Proposta de Serviço - Ultragaz",
        author="Usinagem Luminox",
    )

    styles = getSampleStyleSheet()

    st_small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8.6, leading=10)
    st_small_b = ParagraphStyle("small_b", parent=st_small, fontName="Helvetica-Bold")

    st_title = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=12.5,
        leading=14,
        fontName="Helvetica-Bold",
        alignment=1,  # center
    )

    st_section = ParagraphStyle(
        "section",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=11,
        fontName="Helvetica-Bold",
        alignment=1,
    )

    # Cores (aprox. do template)
    grey = colors.HexColor("#D9D9D9")
    grey2 = colors.HexColor("#EFEFEF")
    blue_qty = colors.HexColor("#D9E2F3")  # coluna de qtde

    # Dados da empresa (fixos por enquanto)
    empresa_nome = "USINAGEM LUMINOX"
    empresa_sub = "SERVIÇOS DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"
    empresa_cnpj = "CNPJ: 18.147.590/0001-45"
    empresa_end = "Rua Padre Alfredo Nesi, n° 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    empresa_contato = "Contato: (85) 9 8566 2160"
    empresa_email = "Email: usiluminox@gmail.com"

    # Campos do orçamento
    numero = getattr(orcamento, "numero", None) or getattr(orcamento, "codigo", None) or getattr(orcamento, "id", None)
    revisao = getattr(orcamento, "revisao", None) or getattr(orcamento, "revisao_num", None) or "0"
    data_emissao = getattr(orcamento, "criado_em", None) or getattr(orcamento, "created_at", None)
    validade = getattr(orcamento, "validade", None) or getattr(orcamento, "validade_em", None)

    # Cliente (puxa o que existir)
    cli_nome = getattr(cliente, "nome", None) or getattr(cliente, "name", None) or "-"
    cli_cnpj = getattr(cliente, "cnpj", None) or "-"
    cli_endereco = getattr(cliente, "endereco", None) or "-"
    cli_cidade = getattr(cliente, "cidade", None) or "-"
    cli_contato = getattr(cliente, "contato", None) or "-"
    cli_emails = getattr(cliente, "email", None) or "-"
    cli_ie = getattr(cliente, "ie", None) or getattr(cliente, "inscricao_estadual", None) or "-"
    cli_cep = getattr(cliente, "cep", None) or "-"
    cli_bairro = getattr(cliente, "bairro", None) or "-"
    cli_estado = getattr(cliente, "estado", None) or "-"

    elements: list[Any] = []

    # -------------------------------------------------
    # Header (empresa)
    # -------------------------------------------------
    top_tbl = Table(
        [
            [Paragraph(f"<b>{empresa_nome}</b>", st_small_b)],
            [Paragraph(empresa_sub, st_small)],
            [Paragraph(empresa_cnpj, st_small)],
            [Paragraph(empresa_end, st_small)],
            [Paragraph(empresa_contato, st_small)],
            [Paragraph(empresa_email, st_small)],
        ],
        colWidths=[190 * mm],
    )
    top_tbl.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    elements.append(top_tbl)
    elements.append(Spacer(1, 6))

    # -------------------------------------------------
    # Título + dados (nº, revisão, emissão, validade)
    # -------------------------------------------------
    titulo_tbl = Table(
        [
            [
                Paragraph("PROPOSTA DE SERVIÇO", st_title),
            ]
        ],
        colWidths=[190 * mm],
    )
    elements.append(titulo_tbl)

    info_tbl = Table(
        [
            ["Nº:", _escape(str(numero)), "REVISÃO:", _escape(str(revisao))],
            ["EMISSÃO:", _fmt_date(data_emissao), "VALIDADE:", _fmt_date(validade)],
        ],
        colWidths=[20 * mm, 75 * mm, 25 * mm, 70 * mm],
    )
    info_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), grey2),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(info_tbl)
    elements.append(Spacer(1, 8))

    # -------------------------------------------------
    # Dados do cliente (box)
    # -------------------------------------------------
    elements.append(Paragraph("DADOS DO CLIENTE", st_section))
    cliente_tbl = Table(
        [
            ["CLIENTE:", _escape(str(cli_nome)), "CNPJ:", _escape(str(cli_cnpj))],
            ["ENDEREÇO:", _escape(str(cli_endereco)), "I.E:", _escape(str(cli_ie))],
            ["BAIRRO:", _escape(str(cli_bairro)), "CEP:", _escape(str(cli_cep))],
            ["CIDADE:", _escape(str(cli_cidade)), "ESTADO:", _escape(str(cli_estado))],
            ["CONTATO:", _escape(str(cli_contato)), "E-MAIL:", _escape(str(cli_emails))],
        ],
        colWidths=[22 * mm, 83 * mm, 16 * mm, 69 * mm],
    )
    cliente_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), grey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(cliente_tbl)
    elements.append(Spacer(1, 8))

    # -------------------------------------------------
    # Itens
    # -------------------------------------------------
    elements.append(Paragraph("DESCRIÇÃO DO SERVIÇO", st_section))

    header = ["ITEM", "DESCRIÇÃO", "QTD", "VALOR UNIT.", "TOTAL"]
    rows = [header]

    for idx, item in enumerate(itens, start=1):
        desc = getattr(item, "descricao", None) or getattr(item, "descricao_livre", None) or getattr(item, "description", None) or "-"
        qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
        unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or getattr(item, "unit_price", None) or 0
        total_item = getattr(item, "total", None)
        if total_item is None:
            total_item = _to_float(qtd) * _to_float(unit)

        rows.append(
            [
                str(idx),
                _escape(str(desc)),
                _fmt_number(qtd),
                _fmt_money_no_prefix(unit),
                _fmt_money_no_prefix(total_item),
            ]
        )

    t_itens = Table(rows, colWidths=[12 * mm, 110 * mm, 15 * mm, 25 * mm, 25 * mm])
    t_itens.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                # Coluna QTD em azul (template)
                ("BACKGROUND", (2, 1), (2, -1), blue_qty),

                ("ALIGN", (2, 1), (4, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(t_itens)

    # -------------------------------------------------
    # Totais
    # -------------------------------------------------
    elements.append(Spacer(1, 8))

    subtotal = getattr(orcamento, "subtotal", None)
    desconto = getattr(orcamento, "desconto", None)
    acrescimo = getattr(orcamento, "acrescimo", None) or getattr(orcamento, "acréscimo", None)
    total = getattr(orcamento, "total", None)

    if subtotal is None:
        subtotal = _sum_totais_itens(itens)
    if total is None:
        total = _to_float(subtotal) + _to_float(acrescimo) - _to_float(desconto)

    totals_data = [
        ["SUBTOTAL", _fmt_money_no_prefix(subtotal)],
        ["DESCONTO", _fmt_money_no_prefix(desconto)],
        ["ACRÉSCIMO", _fmt_money_no_prefix(acrescimo)],
        ["TOTAL", _fmt_money_no_prefix(total)],
    ]
    totals_tbl = Table(totals_data, colWidths=[30 * mm, 30 * mm], hAlign="RIGHT")
    totals_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.0),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("LINEABOVE", (0, 0), (-1, 0), 1.2, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 1.2, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(totals_tbl)

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


# ----------------------------
# Helpers
# ----------------------------

def _fmt_date(v: Any) -> str:
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


def _fmt_number(v: Any) -> str:
    try:
        n = float(v)
        if abs(n - int(n)) < 1e-9:
            return str(int(n))
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0"


def _fmt_money_no_prefix(v: Any) -> str:
    if v is None:
        return "0,00"
    try:
        n = float(v)
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _to_float(v: Any) -> float:
    try:
        if v is None:
            return 0.0
        return float(v)
    except Exception:
        return 0.0


def _sum_totais_itens(itens: Iterable[Any]) -> float:
    total = 0.0
    for item in itens:
        t = getattr(item, "total", None)
        if t is None:
            qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
            unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or getattr(item, "unit_price", None) or 0
            t = _to_float(qtd) * _to_float(unit)
        total += _to_float(t)
    return total
