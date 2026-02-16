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
    fmt_money,
    fmt_number,
    safe_add,
    sum_totais_itens,
    to_float,
)
from ..shared.styles import PDF_FORMAT_PADRAO
from ..shared.assets import build_logo_image


def render_pdf_padrao(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout PADRÃO (modelo Usinagem Luminox).
    Agora com logomarca no cabeçalho (65mm).
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

    empresa_end = "Rua Padre Alfredo Nesi, 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    empresa_doc = "CNPJ: 18.147.590/0001-45"
    empresa_fone = "- Fone: (85) 98566-2160"
    empresa_email = "- Email: usiluminox@gmail.com"

    # ✅ Ajuste (2): estilo justificado para os textos do bloco esquerdo
    st_small_just = ParagraphStyle(
        name="SmallJust",
        parent=st_small,
        alignment=4,  # 4 = JUSTIFY
    )

    # ✅ Ajuste (1): texto do "SERVIÇO DE..." em negrito
    st_small_just_bold = ParagraphStyle(
        name="SmallJustBold",
        parent=st_small_just,
        fontName="Helvetica-Bold",
    )

    # Logo grande (~65mm). Se não existir o arquivo, cai no texto padrão.
    logo = build_logo_image(width_mm=65.0)

    left_block = []
    if logo:
        left_block.append(logo)
        left_block.append(Spacer(1, 3))
        # ✅ (1) negrito + ✅ (2) justificado
        left_block.append(Paragraph(escape(empresa_sub), st_small_just_bold))
    else:
        left_block.append(Paragraph(empresa_nome, st_title_big))
        # ✅ (1) negrito + ✅ (2) justificado
        left_block.append(Paragraph(escape(empresa_sub), st_small_just_bold))

    left_block += [
        Spacer(1, 3),
        # ✅ (2) justificado
        Paragraph(escape(empresa_end), st_small_just),
        Paragraph(
            escape(f"{empresa_doc}  {empresa_fone}  {empresa_email}"),
            st_small_just,
        ),
    ]

    numero = getattr(orcamento, "numero", None) or getattr(orcamento, "codigo", None) or getattr(orcamento, "id", None)
    data_criacao = getattr(orcamento, "criado_em", None) or getattr(orcamento, "created_at", None)

    # ✅ (5) "Proposta de Serviço" e "n.º" com fonte maior
    st_right_title = ParagraphStyle(
        name="RightTitle",
        parent=st_label,
        alignment=2,  # RIGHT
        fontSize=16,  # maior
        leading=16,
    )
    st_right_line = ParagraphStyle(
        name="RightLine",
        parent=st_label,
        alignment=2,  # RIGHT
        fontSize=14,  # maior
        leading=14,
    )
    st_right_date = ParagraphStyle(
        name="RightDate",
        parent=st_label,
        alignment=2,  # RIGHT
        fontSize=11,
        leading=13,
    )

    # ✅ (3) mais espaçamento entre "Proposta / n.º / data"
    # ✅ (4) "Página 1 de 1" fica no rodapé do bloco direito (empurrado pra baixo)
    right_block = [
        Paragraph("<b>Proposta de Serviço</b>", st_right_title),
        Spacer(1, 6),  # ✅ espaçamento maior
        Paragraph(f"n.º <b>{escape(str(numero))}</b>", st_right_line),
        Spacer(1, 6),  # ✅ espaçamento maior
        Paragraph(fmt_date(data_criacao), st_right_date),

        Spacer(1, 38),  # ✅ empurra o "Página 1 de 1" para o final do bloco
        Paragraph("Página 1 de 1", ParagraphStyle("RightPage", parent=st_small, alignment=2)),
    ]

    header_tbl = Table([[left_block, right_block]], colWidths=[125 * mm, 65 * mm])
    header_tbl.setStyle(
        header_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),

                    # ✅ Retângulo com contorno em todos os lados (modelo original)
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.black),

                    # (Opcional) Linha vertical separando as 2 colunas (fica bem parecido com modelo)
                    #("LINEAFTER", (0, 0), (0, 0), 0.6, colors.black),

                    # ✅ Respiro interno para não “grudar” no contorno
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
    )
    elements.append(header_tbl)
    #elements.append(_hr())
    #elements.append(Spacer(1, 6))

    # -------------------------
    # 1) DADOS DO CLIENTE
    # -------------------------
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("1. DADOS DO CLIENTE:", st_section))

    # Campos (o que existir no seu schema/model)
    cli_nome = getattr(cliente, "nome", None) or getattr(cliente, "name", None) or "-"
    cli_endereco = getattr(cliente, "endereco", None) or getattr(cliente, "address", None) or "-"
    cli_bairro = getattr(cliente, "bairro", None) or "-"
    cli_cidade = getattr(cliente, "cidade", None) or "-"
    cli_estado = getattr(cliente, "estado", None) or "-"
    cli_cep = getattr(cliente, "cep", None) or "-"

    cli_cnpj = getattr(cliente, "cnpj", None) or "-"
    cli_ie = getattr(cliente, "ie", None) or getattr(cliente, "inscricao_estadual", None) or "-"
    cli_fone = getattr(cliente, "telefone", None) or getattr(cliente, "fone", None) or "-"
    cli_contato = getattr(cliente, "contato", None) or "-"
    cli_email = getattr(cliente, "email", None) or "-"

    # Tabela em 4 colunas: Label/Valor (esq) + Label/Valor (dir)
    # Largura total = 190mm (mesma área útil do cabeçalho nesse layout)
    dados_cliente = [
        # Linha 0: Cliente (label na col 0) + nome mesclado nas col 1..3
        ["Cliente:", escape(str(cli_nome)), "", ""],

        # Linhas seguintes: coluna esquerda + coluna direita
        ["Endereço:", escape(str(cli_endereco)), "CNPJ:", escape(str(cli_cnpj))],
        ["Bairro:", escape(str(cli_bairro)), "I.E:", escape(str(cli_ie))],
        ["Cidade:", escape(str(cli_cidade)), "Telefone:", escape(str(cli_fone))],
        ["Estado:", escape(str(cli_estado)), "Contato:", escape(str(cli_contato))],
        ["CEP:", escape(str(cli_cep)), "E-mail:", escape(str(cli_email))],
    ]

    tbl_cli = Table(
        dados_cliente,
        colWidths=[18 * mm, 77 * mm, 18 * mm, 77 * mm],  # 18+77+18+77 = 190mm
    )

    tbl_cli.setStyle(
        TableStyle(
            [
                # ✅ Contorno completo
                ("BOX", (0, 0), (-1, -1), 0.8, colors.black),

                # ✅ Mescla SOMENTE o nome do cliente (col 1..3)
                ("SPAN", (1, 0), (3, 0)),

                # Grid interno leve (opcional, mas fica bem “pro”)
                #("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),

                # ✅ linhas horizontais internas (contínuas)
                ("LINEBELOW", (0, 0), (3, 0), 0.25, colors.grey),
                ("LINEBELOW", (0, 1), (3, 1), 0.25, colors.grey),
                ("LINEBELOW", (0, 2), (3, 2), 0.25, colors.grey),
                ("LINEBELOW", (0, 3), (3, 3), 0.25, colors.grey),
                ("LINEBELOW", (0, 4), (3, 4), 0.25, colors.grey),

                # ✅ Estilo geral
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),

                # ✅ Rótulos em negrito (col 0 linhas 0..fim e col 2 linhas 1..fim)
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),

                # ✅ Fundo cinza claro nos rótulos (inclui Cliente)
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFEFEF")),
                ("BACKGROUND", (2, 1), (2, -1), colors.HexColor("#EFEFEF")),
            ]
        )
    )

    elements.append(tbl_cli)

    # -------------------------
    # 2) DESCRIÇÃO DOS SERVIÇOS
    # -------------------------
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("2. DESCRIÇÃO DOS SERVIÇOS:", st_section))

    # Larguras em mm somando 190mm (mesma largura da tabela de cliente)
    # 12 + 15 + 90 + 23 + 25 + 25 = 190mm
    COLS_ITENS = [12 * mm, 12 * mm, 90 * mm, 26 * mm, 25 * mm, 25 * mm]

    rows = [["ITEM", "QTD", "DESCRIÇÃO", "TIPO/SERVIÇO", "VALOR UNIT.", "TOTAL"]]

    for idx, item in enumerate(itens, start=1):
        tipo_servico = (
            getattr(item, "tipo_servico", None)
            or getattr(item, "tipo", None)
            or getattr(item, "categoria", None)
            or "USINAGEM"
        )
        desc = (
            getattr(item, "descricao", None)
            or getattr(item, "descricao_livre", None)
            or getattr(item, "description", None)
            or "-"
        )
        qtd = getattr(item, "quantidade", None) or getattr(item, "qtd", None) or 0
        unit = (
            getattr(item, "valor_unitario", None)
            or getattr(item, "preco_unitario", None)
            or getattr(item, "unit_price", None)
            or 0
        )
        total_item = getattr(item, "total", None)
        if total_item is None:
            total_item = to_float(qtd) * to_float(unit)

        rows.append(
            [
                str(idx),
                fmt_number(qtd),
                escape(str(desc)),
                escape(str(tipo_servico)),
                fmt_money(unit),         # ✅ com R$
                fmt_money(total_item),   # ✅ com R$
            ]
        )

    t_itens = Table(rows, colWidths=COLS_ITENS)
    t_itens.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.0),

                # ✅ Zebra striping (linhas 1..fim). Alterna branco/cinza claro.
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),

                # ✅ Grid interno cinza
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                
                # ✅ Contorno completo
                ("BOX", (0, 0), (-1, -1), 0.8, colors.black),

                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                # ✅ Centralizar colunas 0,1,3,4 e 5 (cabeçalho e itens)
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (3, 0), (3, -1), "CENTER"),
                ("ALIGN", (4, 0), (4, -1), "CENTER"),
                ("ALIGN", (5, 0), (5, -1), "CENTER"),

                # ✅ Descrição mantém à esquerda (melhor leitura)
                ("ALIGN", (2, 0), (2, -1), "LEFT"),

                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(t_itens)

    # -------------------------
    # Totais abaixo da coluna TOTAL
    # -------------------------
    elements.append(Spacer(1, 4))

    subtotal = getattr(orcamento, "subtotal", None)
    desconto = getattr(orcamento, "desconto", None)
    total = getattr(orcamento, "total", None)

    if subtotal is None:
        subtotal = sum_totais_itens(itens)
    if total is None:
        # total = subtotal - desconto (sem acréscimo aqui, conforme seu pedido)
        total = to_float(subtotal) - to_float(desconto)

    rows_totais = [
        ["", "", "", "", "SUBTOTAL:", fmt_money(subtotal)],
        ["", "", "", "", "DESCONTO:", fmt_money(desconto)],
        ["", "", "", "", "TOTAL:", fmt_money(total)],
    ]

    tbl_totais_abaixo = Table(rows_totais, colWidths=COLS_ITENS)
    tbl_totais_abaixo.setStyle(
        TableStyle(
            [
                # sem grid para ficar “limpo” (só alinhado)
                ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),
                ("FONTNAME", (5, -1), (5, -1), "Helvetica-Bold"),

                ("FONTSIZE", (0, 0), (-1, -1), 9.0),

                # alinhar rótulos/valores sob a coluna TOTAL
                ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                ("ALIGN", (5, 0), (5, -1), "CENTER"),

                # um leve respiro
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elements.append(tbl_totais_abaixo)

    # -------------------------
    # 3) CONDIÇÕES COMERCIAIS
    # -------------------------
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("3. CONDIÇÕES COMERCIAIS.", st_section))
    elements.append(_hr())
    elements.append(Spacer(1, 8))

    # Prazo (dias úteis) vem do banco; fallback = 20
    prazo_dias_uteis = (
        getattr(orcamento, "prazo_dias_uteis", None)
        or getattr(orcamento, "prazo_execucao_dias_uteis", None)
        or getattr(orcamento, "prazo_execucao", None)
        or 20
    )
    try:
        prazo_dias_uteis = int(prazo_dias_uteis)
    except Exception:
        prazo_dias_uteis = 20

    # Estilo para rótulo e valor
    st_cond_label = ParagraphStyle(
        name="CondLabel",
        parent=st_small,
        fontName="Helvetica-Bold",
        leading=12,
    )
    st_cond_value = ParagraphStyle(
        name="CondValue",
        parent=st_small,
        leading=12,
    )

    # Dados (rótulo | valor)
    cond_rows = [
        [Paragraph("PRAZO DE EXECUÇÃO:", st_cond_label),
        Paragraph(f"{prazo_dias_uteis} DIAS ÚTEIS (APÓS A APROVAÇÃO DO PEDIDO).", st_cond_value)],

        [Paragraph("VALIDADE DA PROPOSTA:", st_cond_label),
        Paragraph("10 DIAS.", st_cond_value)],

        [Paragraph("FORMA DE PAGAMENTO:", st_cond_label),
        Paragraph("FATURADO PARA 30 DIAS.", st_cond_value)],

        [Paragraph("COLETA E ENTREGA:", st_cond_label),
        Paragraph("POR CONTA DA CONTRATANTE.", st_cond_value)],
    ]

    # Largura total = 190mm (mesma das outras tabelas)
    # Ajuste fino: 55mm para rótulo costuma ficar ótimo
    cond_tbl = Table(cond_rows, colWidths=[55 * mm, 135 * mm])

    cond_tbl.setStyle(
        TableStyle(
            [
                # Sem grid (mais clean), mas com um leve espaçamento
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),

                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                # (Opcional) fundo cinza nos rótulos, igual você fez nos outros blocos
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFEFEF")),
            ]
        )
    )

    elements.append(cond_tbl)

    doc.build(elements, onFirstPage=_draw_footer_assinaturas, onLaterPages=_draw_footer_assinaturas)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def _hr() -> Table:
    """Linha horizontal simples (hack com tabela)."""
    t = Table([[""]], colWidths=[190 * mm], rowHeights=[0.8])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black)]))
    return t

def _draw_footer_assinaturas(canvas, doc) -> None:
    """
    Desenha o rodapé fixo na parte de baixo da página (não depende do fluxo do documento).
    """
    canvas.saveState()

    # Área útil do documento
    left = doc.leftMargin
    right = doc.pagesize[0] - doc.rightMargin
    width = right - left

    # Posição Y fixa a partir da margem inferior (ajuste fino aqui)
    # Quanto maior, mais "subido". Quanto menor, mais perto do fim da folha.
    y = doc.bottomMargin + 14 * mm

    # Larguras das colunas (2 colunas iguais)
    col_w = width / 2.0
    gap = 8 * mm  # respiro entre colunas
    col_w = (width - gap) / 2.0

    # Coordenadas de cada coluna
    x_left = left
    x_right = left + col_w + gap

    # Estilos (centralizados)
    styles = getSampleStyleSheet()
    st = ParagraphStyle("FBase", parent=styles["Normal"], fontSize=9, leading=11)
    st_center = ParagraphStyle("FCenter", parent=st, alignment=1)  # CENTER
    st_bold_center = ParagraphStyle("FBoldCenter", parent=st_center, fontName="Helvetica-Bold")
    st_bold = ParagraphStyle("FBold", parent=st, fontName="Helvetica-Bold")

    # --- Coluna esquerda ---
    left_flow = [
        Paragraph("Atenciosamente,", st_bold),
        Spacer(1, 41),
        Paragraph("________________________________________", st_center),
        Spacer(1, 2),
        Paragraph("Fco. Jackson Almeida de Oliveira", st_bold_center),
        Paragraph("Diretor Técnico - Usinagem Luminox", st_center),
    ]

    # --- Coluna direita ---
    right_flow = [
        Paragraph("Proposta Autorizada por:", st_bold),
        Spacer(1, 10),
        Paragraph("Data: ______ / ______ / ______", st),
        Spacer(1, 20),
        Paragraph("________________________________________", st_center),
        Spacer(1, 2),
        Paragraph("(Dispensa assinatura, se aprovado por e-mail)", st_center),
    ]

    # Desenhar usando "Frames" (sem precisar mexer no fluxo do documento)
    from reportlab.platypus import Frame

    # Altura reservada para o rodapé (ajuste fino)
    footer_h = 38 * mm

    f_left = Frame(x_left, y, col_w, footer_h, showBoundary=0)
    f_right = Frame(x_right, y, col_w, footer_h, showBoundary=0)

    f_left.addFromList(left_flow, canvas)
    f_right.addFromList(right_flow, canvas)

    # ---------------------------------------------------------
    # Linha + dados da empresa fixos no final da página (rodapé)
    # ---------------------------------------------------------
    # Ajuste fino: quanto maior, mais "sobe" a linha/texto.
    y_line = doc.bottomMargin + 10 * mm

    canvas.setLineWidth(0.8)
    canvas.setStrokeColor(colors.black)
    canvas.line(left, y_line, right, y_line)

    # Texto do rodapé (2 linhas), centralizado
    footer_line1 = "Rua Padre Alfredo Nesi, 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    footer_line2 = "CNPJ: 18.147.590/0001-45 - Fone: (85) 98566-2160 - Email: usiluminox@gmail.com"

    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica", 7.8)

    # Posição das linhas de texto (abaixo da linha)
    y_text_1 = doc.bottomMargin + 5.0 * mm
    y_text_2 = doc.bottomMargin + 1.0 * mm

    x_center = left + (width / 2.0)

    canvas.drawCentredString(x_center, y_text_1, footer_line1)
    canvas.drawCentredString(x_center, y_text_2, footer_line2)

    canvas.restoreState()
