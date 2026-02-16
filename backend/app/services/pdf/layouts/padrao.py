from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from ..shared.helpers import (
    escape,
    fmt_date,
    fmt_money_no_prefix,
    fmt_number,
    safe_add,
    sum_totais_itens,
    to_float,
)
from ..shared.styles import PDF_FORMAT_PADRAO


def render_pdf_padrao(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout PADRÃO (modelo Usinagem Luminox).
    Mantém o mesmo desenho que já estava funcionando, mas agora
    reutilizando helpers/styles compartilhados.
    """
    buf = BytesIO()
    fmt = PDF_FORMAT_PADRAO

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
    empresa_nome = "USINAGEM LUMINOX"
    empresa_sub = "SERVIÇO DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"

    empresa_end = "Rua Padre Alfredo Nesi, n° 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    empresa_doc = "CNPJ: 18.147.590/0001-45"
    empresa_fone = "Fone: (85) 98566-2160"
    empresa_email = "Email: usiluminox@gmail.com"

    left_block = [
        Paragraph(empresa_nome, st_title_big),
        Paragraph(empresa_sub, st_small),
        Spacer(1, 3),
        Paragraph(empresa_end, st_small),
        Paragraph(
            f"{empresa_doc} &nbsp;&nbsp;&nbsp; {empresa_fone} &nbsp;&nbsp;&nbsp; {empresa_email}",
            st_small,
        ),
    ]

    numero = getattr(orcamento, "numero", None) or getattr(orcamento, "codigo", None) or getattr(orcamento, "id", None)
    data_criacao = getattr(orcamento, "criado_em", None) or getattr(orcamento, "created_at", None)

    right_block = [
        Paragraph("<b>Proposta de Serviço</b>", ParagraphStyle("RightTitle", parent=st_label, alignment=2, fontSize=12)),
        Paragraph(f"n.º <b>{escape(str(numero))}</b>", ParagraphStyle("RightLine", parent=st_label, alignment=2)),
        Paragraph(fmt_date(data_criacao), ParagraphStyle("RightLine2", parent=st_label, alignment=2)),
        Spacer(1, 2),
        Paragraph("Página 1 de 1", ParagraphStyle("RightPage", parent=st_small, alignment=2)),
    ]

    header_tbl = Table([[left_block, right_block]], colWidths=[135 * mm, 55 * mm])
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

    elements.append(Spacer(1, 6))
    elements.append(_hr())
    elements.append(Spacer(1, 6))

    # -------------------------
    # 1) Dados do Cliente
    # -------------------------
    elements.append(Paragraph("1. Dados do Cliente:", st_section))

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
        ["Cliente:", escape(str(cli_nome)), "CNPJ:", escape(str(cli_cnpj))],
        ["Endereço:", escape(str(cli_endereco)), "I.E:", escape(str(cli_ie))],
        ["Bairro:", escape(str(cli_bairro)), "Cep:", escape(str(cli_cep))],
        ["Cidade:", escape(str(cli_cidade)), "Contato:", escape(str(cli_contato))],
        ["Estado:", escape(str(cli_estado)), "E-mail:", escape(str(cli_email))],
        ["Fone:", escape(str(cli_fone)), "", ""],
    ]

    tbl_cli = Table(dados_cliente, colWidths=[18 * mm, 92 * mm, 14 * mm, 62 * mm])
    tbl_cli.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(tbl_cli)

    # -------------------------
    # 2) Itens
    # -------------------------
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("2. DESCRIÇÃO DO SERVIÇO:", st_section))

    rows = [["ITEM", "DESCRIÇÃO", "QTD", "VALOR UNIT.", "TOTAL"]]

    for idx, item in enumerate(itens, start=1):
        desc = getattr(item, "descricao", None) or getattr(item, "descricao_livre", None) or getattr(item, "description", None) or "-"
        qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
        unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or getattr(item, "unit_price", None) or 0
        total_item = getattr(item, "total", None)
        if total_item is None:
            total_item = to_float(qtd) * to_float(unit)

        rows.append([str(idx), escape(str(desc)), fmt_number(qtd), fmt_money_no_prefix(unit), fmt_money_no_prefix(total_item)])

    t_itens = Table(rows, colWidths=[12 * mm, 110 * mm, 15 * mm, 25 * mm, 25 * mm])
    t_itens.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9.0),
                ("FONTSIZE", (0, 1), (-1, -1), 9.0),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (2, 1), (4, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(t_itens)

    # -------------------------
    # Totais
    # -------------------------
    elements.append(Spacer(1, 8))

    subtotal = getattr(orcamento, "subtotal", None)
    desconto = getattr(orcamento, "desconto", None)
    acrescimo = getattr(orcamento, "acrescimo", None) or getattr(orcamento, "acréscimo", None)
    total = getattr(orcamento, "total", None)

    if subtotal is None:
        subtotal = sum_totais_itens(itens)
    if total is None:
        total = safe_add(safe_add(subtotal, acrescimo), -to_float(desconto))

    totals_data = [
        ["SUBTOTAL", fmt_money_no_prefix(subtotal)],
        ["DESCONTO", fmt_money_no_prefix(desconto)],
        ["ACRÉSCIMO", fmt_money_no_prefix(acrescimo)],
        ["TOTAL", fmt_money_no_prefix(total)],
    ]
    totals_tbl = Table(totals_data, colWidths=[30 * mm, 30 * mm], hAlign="RIGHT")
    totals_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
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

    condicoes = [
        "PRAZO DE EXECUÇÃO: 20 DIAS ÚTEIS (APÓS A APROVAÇÃO DO PEDIDO)",
        "VALIDADE DA PROPOSTA: 10 DIAS",
        "* COLETA E ENTREGA SERÁ POR CONTA DA EMPRESA CONTRATANTE.",
    ]
    for linha in condicoes:
        elements.append(Paragraph(escape(linha), st_small))

    # -------------------------
    # Rodapé (assinaturas)
    # -------------------------
    elements.append(Spacer(1, 18))
    elements.append(Paragraph("Atenciosamente,", st_label))
    elements.append(Spacer(1, 10))

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

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def _hr() -> Table:
    """Linha horizontal simples (hack com tabela)."""
    t = Table([[""]], colWidths=[190 * mm], rowHeights=[0.8])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black)]))
    return t
