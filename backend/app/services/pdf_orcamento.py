"""
Geração de PDF de Orçamento (layout PADRÃO) - modelo Usinagem Luminox.

Baseado no arquivo modelo enviado (LAYOUT_PADRÃO.pdf):
- Cabeçalho com nome da empresa e dados (endereço, CNPJ, fone, e-mail)
- Título "Proposta de Serviço" + nº + data (à direita)
- Seção 1: Dados do Cliente (box)
- Seção 2: Descrição do Serviço (tabela itens)
- Totais (à direita)
- Seção 3: Condições comerciais (texto fixo)
- Rodapé com assinatura

Dependência: reportlab
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from io import BytesIO
from typing import Any, Iterable

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# Identificadores de layout (estrutura pronta p/ futuro)
LAYOUT_PADRAO = "PADRAO"
LAYOUT_ACO_CEARENSE = "ACO_CEARENSE"
LAYOUT_ULTRAGAZ = "ULTRAGAZ"


def escolher_layout_cliente(cliente: Any) -> str:
    """
    Nesta etapa: sempre PADRAO, mas pronto para evoluir.
    """
    return LAYOUT_PADRAO


def generate_orcamento_pdf(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    layout = escolher_layout_cliente(cliente)
    if layout == LAYOUT_PADRAO:
        return _render_pdf_padrao_modelo_luminox(orcamento, itens, cliente)
    return _render_pdf_padrao_modelo_luminox(orcamento, itens, cliente)


@dataclass(frozen=True)
class PdfOrcamentoFormat:
    page_size = A4
    left_margin = 12 * mm
    right_margin = 12 * mm
    top_margin = 10 * mm
    bottom_margin = 12 * mm


# ----------------------------
# Layout PADRÃO (modelo Luminox)
# ----------------------------

def _render_pdf_padrao_modelo_luminox(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    buf = BytesIO()
    fmt = PdfOrcamentoFormat()

    doc = SimpleDocTemplate(
        buf,
        pagesize=fmt.page_size,
        leftMargin=fmt.left_margin,
        rightMargin=fmt.right_margin,
        topMargin=fmt.top_margin,
        bottomMargin=fmt.bottom_margin,
        title="Proposta de Serviço",
        author="Usinagem Luminox",
    )

    styles = getSampleStyleSheet()

    # Títulos/estilos
    st_title_big = ParagraphStyle(
        name="TitleBig",
        parent=styles["Title"],
        fontSize=20,
        leading=22,
        spaceAfter=2,
    )
    st_small = ParagraphStyle(
        name="Small",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
    )
    st_section = ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontSize=10.5,
        leading=12,
        spaceBefore=8,
        spaceAfter=4,
    )
    st_label = ParagraphStyle(
        name="Label",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
    )

    elements: list[Any] = []

    # -------------------------
    # Cabeçalho (2 colunas)
    # -------------------------
    # Esquerda: nome + subtítulo + dados (endereço/cnpj/fone/email)
    empresa_nome = "USINAGEM LUMINOX"
    empresa_sub = "SERVIÇO DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"

    # (Por enquanto fixo, depois podemos ler de config/.env)
    empresa_end = "Rua Padre Alfredo Nesi, n° 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    empresa_doc = "CNPJ: 18.147.590/0001-45"
    empresa_fone = "Fone: (85) 98566-2160"
    empresa_email = "Email: usiluminox@gmail.com"

    left_block = [
        Paragraph(empresa_nome, st_title_big),
        Paragraph(empresa_sub, st_small),
        Spacer(1, 3),
        Paragraph(empresa_end, st_small),
        Paragraph(f"{empresa_doc} &nbsp;&nbsp;&nbsp; {empresa_fone} &nbsp;&nbsp;&nbsp; {empresa_email}", st_small),
    ]

    # Direita: "Proposta de Serviço" + nº + data + página
    # Número no modelo: "n.º 292/24" (vamos mapear do campo "numero" se existir; senão usa ID)
    numero = getattr(orcamento, "numero", None) or getattr(orcamento, "codigo", None) or getattr(orcamento, "id", None)
    # data do orçamento (criado_em)
    data_criacao = getattr(orcamento, "criado_em", None) or getattr(orcamento, "created_at", None)

    right_block = [
        Paragraph("<b>Proposta de Serviço</b>", ParagraphStyle("RightTitle", parent=st_label, alignment=2, fontSize=12)),
        Paragraph(f"n.º <b>{_escape(str(numero))}</b>", ParagraphStyle("RightLine", parent=st_label, alignment=2)),
        Paragraph(_fmt_date(data_criacao), ParagraphStyle("RightLine2", parent=st_label, alignment=2)),
        Spacer(1, 2),
        Paragraph("Página 1 de 1", ParagraphStyle("RightPage", parent=st_small, alignment=2)),  # simples por enquanto
    ]

    header_tbl = Table(
        [[left_block, right_block]],
        colWidths=[135 * mm, 55 * mm],
    )
    header_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elements.append(header_tbl)

    # Linha separadora
    elements.append(Spacer(1, 6))
    elements.append(_hr())
    elements.append(Spacer(1, 6))

    # -------------------------
    # 1) Dados do Cliente (box)
    # -------------------------
    elements.append(Paragraph("1. Dados do Cliente:", st_section))

    # Campos (o que existir no seu schema/model)
    cli_nome = getattr(cliente, "nome", None) or getattr(cliente, "name", None) or "-"
    cli_endereco = getattr(cliente, "endereco", None) or getattr(cliente, "address", None) or "-"
    cli_cnpj = getattr(cliente, "cnpj", None) or "-"
    cli_ie = getattr(cliente, "ie", None) or getattr(cliente, "inscricao_estadual", None) or "-"
    cli_bairro = getattr(cliente, "bairro", None) or "-"
    cli_cidade = getattr(cliente, "cidade", None) or "-"
    cli_cep = getattr(cliente, "cep", None) or "-"
    cli_estado = getattr(cliente, "estado", None) or "-"
    cli_contato = getattr(cliente, "contato", None) or "-"
    cli_fone = getattr(cliente, "telefone", None) or getattr(cliente, "fone", None) or "-"
    cli_email = getattr(cliente, "email", None) or "-"

    dados_cliente = [
        ["Cliente:", _escape(str(cli_nome)), "CNPJ:", _escape(str(cli_cnpj))],
        ["Endereço:", _escape(str(cli_endereco)), "I.E:", _escape(str(cli_ie))],
        ["Bairro:", _escape(str(cli_bairro)), "Cep:", _escape(str(cli_cep))],
        ["Cidade:", _escape(str(cli_cidade)), "Contato:", _escape(str(cli_contato))],
        ["Estado:", _escape(str(cli_estado)), "E-mail:", _escape(str(cli_email))],
        ["Fone:", _escape(str(cli_fone)), "", ""],
    ]

    box = Table(dados_cliente, colWidths=[20 * mm, 85 * mm, 20 * mm, 65 * mm])
    box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.2, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(box)

    # -------------------------
    # 2) Descrição do Serviço
    # -------------------------
    elements.append(Paragraph("2. Descrição do Serviço", st_section))

    # Linha "Última atualização" (no modelo)
    ultima_atualizacao = getattr(orcamento, "atualizado_em", None) or getattr(orcamento, "updated_at", None)
    if ultima_atualizacao:
        elements.append(
            Paragraph(f"<b>Última atualização:</b> {_fmt_date(ultima_atualizacao)}", st_small)
        )
        elements.append(Spacer(1, 3))

    # Tabela itens conforme modelo
    itens_table_data: list[list[str]] = [
        ["Item", "Qtde.", "Descrição", "Tipo/Serviço", "Valor Unitário", "Valor Total"]
    ]

    # Tipo/Serviço: no SGU vocês têm "tipo do item" (LIVRE etc).
    # Vamos usar "tipo" se existir no item; senão "Serviço".
    idx = 1
    for item in itens:
        desc = getattr(item, "descricao", None) or getattr(item, "descricao_livre", None) or getattr(item, "description", None) or ""
        qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
        unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or getattr(item, "unit_price", None) or 0
        total_item = getattr(item, "total", None)
        if total_item is None:
            total_item = _to_float(qtd) * _to_float(unit)

        tipo_servico = getattr(item, "tipo_servico", None) or getattr(item, "tipo", None) or getattr(item, "item_tipo", None) or "Serviço"

        itens_table_data.append(
            [
                str(idx),
                _fmt_number(qtd),
                _escape(str(desc)),
                _escape(str(tipo_servico)),
                _fmt_money(unit),
                _fmt_money(total_item),
            ]
        )
        idx += 1

    t_itens = Table(
        itens_table_data,
        colWidths=[10 * mm, 14 * mm, 80 * mm, 32 * mm, 26 * mm, 26 * mm],
        repeatRows=1,
    )
    t_itens.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),

                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.8),

                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("ALIGN", (0, 1), (1, -1), "CENTER"),
                ("ALIGN", (4, 1), (5, -1), "RIGHT"),

                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),

                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#EDEDED")]),
            ]
        )
    )
    elements.append(t_itens)

    # Totais (modelo: Total e Total com Desconto)
    subtotal = getattr(orcamento, "subtotal", None)
    desconto = getattr(orcamento, "desconto", None)
    acrescimo = getattr(orcamento, "acrescimo", None)
    total = getattr(orcamento, "total", None)

    if subtotal is None:
        subtotal = _sum_totais_itens(itens)
    if total is None:
        total = _to_float(subtotal) + _to_float(acrescimo) - _to_float(desconto)

    # % desconto (se existir)
    desconto_pct = getattr(orcamento, "desconto_percentual", None) or getattr(orcamento, "desconto_pct", None)

    totals_rows = [
        ["Total =", _fmt_money(total)],
    ]
    if desconto_pct is not None:
        totals_rows.append([f"Total com Desconto de {desconto_pct} % =", _fmt_money(total)])
    else:
        totals_rows.append(["Total com Desconto =", _fmt_money(total)])

    elements.append(Spacer(1, 6))
    totals_tbl = Table(totals_rows, colWidths=[150 * mm, 40 * mm], hAlign="RIGHT")
    totals_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LINEABOVE", (0, 0), (-1, 0), 1.2, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 1.2, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(totals_tbl)

    # -------------------------
    # 3) Condições comerciais
    # -------------------------
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("3. CONDIÇÕES COMERCIAIS.", st_section))

    # Texto fixo conforme modelo (ajustável depois)
    condicoes = [
        "PRAZO DE EXECUÇÃO: 20 DIAS ÚTEIS (APÓS A APROVAÇÃO DO PEDIDO)",
        "VALIDADE DA PROPOSTA: 10 DIAS",
        "* COLETA E ENTREGA SERÁ POR CONTA DA EMPRESA CONTRATANTE.",
    ]
    for linha in condicoes:
        elements.append(Paragraph(_escape(linha), st_small))

    # -------------------------
    # Rodapé (assinaturas)
    # -------------------------
    elements.append(Spacer(1, 18))
    elements.append(Paragraph("Atenciosamente,", st_label))
    elements.append(Spacer(1, 10))

    # Linhas de assinatura (tabela simples)
    sig_data = [
        ["Contratante", "Proposta Autorizada por:", "______________________________"],
        ["", "Data:", "____/____/_______"],
        ["", "(Dispensa assinatura, se enviado por e-mail)", ""],
        ["Contratada", "", ""],
    ]
    sig_tbl = Table(sig_data, colWidths=[30 * mm, 55 * mm, 95 * mm])
    sig_tbl.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 3), (0, 3), "Helvetica-Bold"),
                ("SPAN", (1, 2), (2, 2)),
                ("ALIGN", (2, 0), (2, 1), "LEFT"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(sig_tbl)

    # Build PDF
    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


# ----------------------------
# Helpers
# ----------------------------

def _hr() -> Table:
    """Linha horizontal simples (hack com tabela)"""
    t = Table([[""]], colWidths=[190 * mm], rowHeights=[0.8])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black)]))
    return t

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

def _fmt_money(v: Any) -> str:
    if v is None:
        return "R$ 0,00"
    try:
        n = float(v)
        s = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {s}"
    except Exception:
        return "R$ 0,00"

def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
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
