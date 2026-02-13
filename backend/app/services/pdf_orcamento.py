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


# normaliza para evitar acentos / variações simples
def _normalize_name(value: str) -> str:
    value = (value or "").strip().lower()
    # normalização simples (sem dependências extras)
    return (
        value.replace("á", "a").replace("ã", "a").replace("â", "a")
        .replace("é", "e").replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o").replace("ô", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def escolher_layout_cliente(cliente: Any) -> str:
    """
    Decide qual layout usar com base no cliente.

    Regras:
    - Aço Cearense -> layout específico (ainda não implementado)
    - Ultragaz -> layout específico (implementado)
    - Demais -> PADRAO
    """
    nome = getattr(cliente, "nome", None) or getattr(cliente, "name", "") or ""
    nome_norm = _normalize_name(str(nome))

    if nome_norm == "aco cearense":
        return LAYOUT_ACO_CEARENSE

    if nome_norm == "ultragaz":
        return LAYOUT_ULTRAGAZ

    return LAYOUT_PADRAO


def generate_orcamento_pdf(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    layout = escolher_layout_cliente(cliente)

    if layout == LAYOUT_PADRAO:
        return _render_pdf_padrao_modelo_luminox(orcamento, itens, cliente)

    if layout == LAYOUT_ULTRAGAZ:
        return _render_pdf_ultragaz(orcamento, itens, cliente)

    # Layout ainda não implementado
    if layout == LAYOUT_ACO_CEARENSE:
        raise NotImplementedError(
            "Layout de PDF específico para Aço Cearense ainda não está disponível."
        )

    raise NotImplementedError("Layout de PDF não suportado.")


@dataclass(frozen=True)
class PdfOrcamentoFormat:
    page_size = A4
    left_margin = 8 * mm
    right_margin = 8 * mm
    top_margin = 8 * mm
    bottom_margin = 8 * mm


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


# -------------------------------------------------------------------
# ULTRAGAZ (novo layout conforme LAYOUT_ULTRAGAZ.pdf)
# -------------------------------------------------------------------

def _render_pdf_ultragaz(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
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
    cli_tel = getattr(cliente, "telefone", None) or getattr(cliente, "fone", None) or "-"

    # Descritivo (no template: texto livre grande)
    descritivo = (
        getattr(orcamento, "descritivo", None)
        or getattr(orcamento, "observacoes", None)
        or getattr(orcamento, "observacao", None)
        or ""
    )

    elements: list[Any] = []

    # ---------------------------
    # 1) Cabeçalho (logo + dados)
    # ---------------------------
    # Logo: por enquanto, placeholder (caixa). Depois colocamos imagem.
    logo_box = Table(
        [[Paragraph("<b>USINAGEM LUMINOX</b>", st_small_b)]],
        colWidths=[60 * mm],
        rowHeights=[18 * mm],
    )
    logo_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    empresa_box = Table(
        [[
            Paragraph(f"<b>{empresa_nome}</b>", st_title),
            Paragraph(empresa_sub, st_small),
            Paragraph(empresa_cnpj, st_small),
            Paragraph(empresa_end, st_small),
            Paragraph(f"{empresa_contato} &nbsp;&nbsp;&nbsp; {empresa_email}", st_small),
        ]],
        colWidths=[120 * mm],
    )
    empresa_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    header_tbl = Table(
        [[logo_box, empresa_box]],
        colWidths=[60 * mm, 120 * mm],
    )
    header_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(header_tbl)

    # ------------------------------------------
    # 2) Linha cinza: proposta/revisao/data/valid
    # ------------------------------------------
    line_tbl = Table(
        [[
            Paragraph("PROPOSTA DE SERVIÇO N° :", st_small_b),
            Paragraph(_escape(str(numero)), st_small),
            Paragraph("REVISÃO N° :", st_small_b),
            Paragraph(_escape(str(revisao)), st_small),
            Paragraph("DATA DE EMISSÃO:", st_small_b),
            Paragraph(_fmt_date(data_emissao), st_small),
            Paragraph("VALIDADE DA PROPOSTA:", st_small_b),
            Paragraph(_fmt_date(validade), st_small),
        ]],
        colWidths=[34 * mm, 16 * mm, 22 * mm, 10 * mm, 26 * mm, 22 * mm, 33 * mm, 17 * mm],
    )
    line_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("ALIGN", (3, 0), (3, 0), "CENTER"),
                ("ALIGN", (5, 0), (5, 0), "CENTER"),
                ("ALIGN", (7, 0), (7, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(line_tbl)

    # ---------------------------
    # 3) DADOS DO CLIENTE (box)
    # ---------------------------
    elements.append(_section_bar("DADOS DO CLIENTE", st_section))

    cliente_tbl = Table(
        [[
            Paragraph(
                f"<b>CLIENTE:</b> {_escape(str(cli_nome))}<br/>"
                f"<b>CNPJ:</b> {_escape(str(cli_cnpj))}<br/>"
                f"<b>ENDEREÇO:</b> {_escape(str(cli_endereco))}<br/>"
                f"<b>CIDADE:</b> {_escape(str(cli_cidade))}<br/>"
                f"<b>CONTATO:</b> {_escape(str(cli_contato))}<br/>"
                f"<b>E-MAILS:</b> {_escape(str(cli_emails))}",
                st_small,
            ),
            Paragraph(
                f"<b>I.E:</b> {_escape(str(cli_ie))}<br/>"
                f"<b>CEP:</b> {_escape(str(cli_cep))}<br/>"
                f"<b>BAIRRO:</b> {_escape(str(cli_bairro))}<br/>"
                f"<b>ESTADO:</b> {_escape(str(cli_estado))}<br/>"
                f"<b>TELEFONE:</b> {_escape(str(cli_tel))}<br/>"
                f"<b>E-MAILS:</b> {_escape(str(cli_emails))}",
                st_small,
            ),
        ]],
        colWidths=[90 * mm, 90 * mm],
    )
    cliente_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), grey2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(cliente_tbl)

    # ---------------------------
    # 4) Tabela de Itens
    # ---------------------------
    elements.append(_section_bar("DESCRIÇÃO DO SERVIÇO", st_section))

    header = ["ITEM", "DESCRIÇÃO DO ITEM", "QTDE", "TIPO SERVIÇO", "VALOR UNIT.", "VALOR TOTAL"]

    rows: list[list[str]] = [header]
    for item in itens:
        cod = getattr(item, "codigo", None) or getattr(item, "id", None) or ""
        desc = getattr(item, "descricao", None) or getattr(item, "descricao_livre", None) or ""
        qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
        tipo = getattr(item, "tipo_servico", None) or getattr(item, "tipo", None) or getattr(item, "item_tipo", None) or "SERVIÇO"
        unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or 0
        total_item = getattr(item, "total", None)
        if total_item is None:
            total_item = _to_float(qtd) * _to_float(unit)

        rows.append([
            str(cod),
            _escape(str(desc)),
            _fmt_number(qtd),
            _escape(str(tipo)),
            _fmt_money(unit),
            _fmt_money(total_item),
        ])

    # Garante “linhas em branco” para ficar visualmente igual ao modelo
    while len(rows) < 13:  # 1 header + ~12 linhas
        rows.append(["", "", "", "", "", ""])

    itens_tbl = Table(
        rows,
        colWidths=[18 * mm, 78 * mm, 14 * mm, 28 * mm, 28 * mm, 28 * mm],
        repeatRows=1,
    )
    itens_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),

                ("BACKGROUND", (0, 0), (-1, 0), blue_qty),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),

                ("FONTSIZE", (0, 1), (-1, -1), 8.6),
                ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),

                ("BACKGROUND", (2, 1), (2, -1), blue_qty),
                ("ALIGN", (2, 1), (2, -1), "CENTER"),

                ("ALIGN", (4, 1), (5, -1), "RIGHT"),

                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(itens_tbl)

    # ---------------------------
    # 5) Totais (faixa cinza)
    # ---------------------------
    subtotal = getattr(orcamento, "subtotal", None)
    desconto = getattr(orcamento, "desconto", None) or 0
    acrescimo = getattr(orcamento, "acrescimo", None) or 0
    total = getattr(orcamento, "total", None)

    if subtotal is None:
        subtotal = _sum_totais_itens(itens)
    if total is None:
        total = _to_float(subtotal) + _to_float(acrescimo) - _to_float(desconto)

    desconto_pct = getattr(orcamento, "desconto_percentual", None) or getattr(orcamento, "desconto_pct", None) or 0

    totals_tbl = Table(
        [
            ["TOTAL GERAL DO SERVIÇO", "R$", _fmt_money_no_prefix(total)],
            ["TOTAL COM DESCONTO DE", f"{desconto_pct}%", "R$", _fmt_money_no_prefix(total)],
        ],
        colWidths=[120 * mm, 10 * mm, 18 * mm, 32 * mm],
    )
    totals_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (2, -1), "CENTER"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(totals_tbl)

    # ---------------------------
    # 6) Descritivo (box)
    # ---------------------------
    elements.append(_section_bar("DESCRITIVO", st_section))

    desc_tbl = Table(
        [[Paragraph(_escape(str(descritivo)) if descritivo else "&nbsp;", st_small)]],
        colWidths=[180 * mm],
        rowHeights=[18 * mm],
    )
    desc_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(desc_tbl)

    # ---------------------------
    # 7) Prazos e condições (box)
    # ---------------------------
    elements.append(_section_bar("PRAZOS E CONDIÇÕES DE PAGAMENTO", st_section))

    prazos_texto = (
        "<b>Prazo de execução:</b> 30 dias, após a aprovação da proposta, a contar do recebimento do material.<br/>"
        "Coleta e entrega inclusos na proposta. Dispensamos assinaturas na proposta, se enviado por e-mail.<br/>"
        "<b>Condição de pagamento:</b> 30 dias, através de transferência bancária."
    )

    prazos_tbl = Table(
        [[Paragraph(prazos_texto, st_small)]],
        colWidths=[180 * mm],
        rowHeights=[22 * mm],
    )
    prazos_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(prazos_tbl)

    # ---------------------------
    # 8) Assinaturas
    # ---------------------------
    elements.append(Spacer(1, 10))

    # Pegamos nomes (se existirem) ou deixamos fixo como no modelo
    nome_contratada = getattr(orcamento, "assinatura_contratada", None) or "Fco Jackson Almeida de Oliveira"
    cargo_contratada = getattr(orcamento, "cargo_contratada", None) or "Diretor Técnico - Luminox"
    nome_contratante = getattr(cliente, "contato", None) or "SUYANE GASPAR"
    razao_contratante = cli_nome

    sig = Table(
        [[
            Paragraph("______________________________", st_small),
            Paragraph("______________________________", st_small),
        ],
         [
            Paragraph(f"<b>{_escape(str(nome_contratada))}</b><br/>{_escape(str(cargo_contratada))}<br/><i>Contratada</i>", st_small),
            Paragraph(f"<b>{_escape(str(nome_contratante))}</b><br/>{_escape(str(razao_contratante))}<br/><i>Contratante</i>", st_small),
         ]],
        colWidths=[90 * mm, 90 * mm],
    )
    sig.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(sig)

    doc.build(elements)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def _section_bar(title: str, style: ParagraphStyle) -> Table:
    t = Table([[Paragraph(title, style)]], colWidths=[180 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, colors.black),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#D9D9D9")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


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


def _fmt_money_no_prefix(v: Any) -> str:
    """Mesma formatação, porém sem 'R$' (o template usa 'R$' em coluna separada)."""
    if v is None:
        return "0,00"
    try:
        n = float(v)
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def _escape(text: str) -> str:
    return (
        str(text).replace("&", "&amp;")
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
            unit = getattr(item, "valor_unitario", None) or getattr(item, "preco_unitario", None) or 0
            t = _to_float(qtd) * _to_float(unit)
        total += _to_float(t)
    return total