from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

from ..shared.assets import build_logo_image
from ..shared.helpers import (
    escape,
    fmt_date,
    fmt_money_no_prefix,
    fmt_number,
    sum_totais_itens,
    to_float,
)
from ..shared.styles import PDF_FORMAT_ULTRAGAZ

def _register_calibri():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))  # .../backend/app
    fonts_dir = os.path.join(base_dir, "assets", "fonts")

    calibri = os.path.join(fonts_dir, "calibri.ttf")
    calibri_b = os.path.join(fonts_dir, "calibrib.ttf")
    calibri_i = os.path.join(fonts_dir, "calibrii.ttf")
    calibri_bi = os.path.join(fonts_dir, "calibriz.ttf")

    if os.path.exists(calibri):
        pdfmetrics.registerFont(TTFont("Calibri", calibri))
    if os.path.exists(calibri_b):
        pdfmetrics.registerFont(TTFont("Calibri-Bold", calibri_b))
    if os.path.exists(calibri_i):
        pdfmetrics.registerFont(TTFont("Calibri-Italic", calibri_i))
    if os.path.exists(calibri_bi):
        pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", calibri_bi))

_register_calibri()

def render_pdf_ultragaz(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout ULTRAGAZ (conforme modelo do cliente).
    - Usa helpers/styles/assets compartilhados (mesmo padrão do padrao.py)
    - Cabeçalho com 2 tabelas (topo 2 colunas + faixa 4 colunas/2 linhas)
    - Box externo em volta da página inteira (área útil)
    """
    buf = BytesIO()
    fmt = PDF_FORMAT_ULTRAGAZ

    # =========================================================
    # TEMA / CORES (ULTRAGAZ) - definido 1x e reutilizado (closure)
    # =========================================================
    theme = {
        "BLACK": colors.black,
        "GRID": colors.HexColor("#A0A0A0"),
        "TITLE_BG": colors.HexColor("#D0CECE"),
        "LIGHT_GRAY": colors.HexColor("#E7E6E6"),
        "LIGHT_BLUE": colors.HexColor("#D9E1F2"),
    }

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

    # ----------------------------
    # Styles (limpos e consistentes)
    # ----------------------------
    FONT = "Calibri"
    FONT_BOLD = "Calibri-Bold"
    FONT_ITALIC = "Calibri-Italic"
    FONT_BOLD_ITALIC = "Calibri-BoldItalic"

    BASE_SIZE = 9
    BASE_LEADING = 13

    TITLE_SIZE = 16
    TITLE_LEADING = 20

    def _make_styles():
        base = ParagraphStyle(
            name="Base",
            parent=styles["Normal"],
            fontName=FONT,
            fontSize=BASE_SIZE,
            leading=BASE_LEADING,
        )
        italic = ParagraphStyle(name="Italic", parent=base, fontName=FONT_ITALIC)
        bold = ParagraphStyle(name="Bold", parent=base, fontName=FONT_BOLD)

        center = ParagraphStyle(name="Center", parent=base, alignment=1)  
        right = ParagraphStyle(name="Right", parent=base, alignment=2)

        bold_italic = ParagraphStyle(name="BoldItalic", parent=base, fontName=FONT_BOLD_ITALIC)
        bold_center = ParagraphStyle(name="BoldCenter", parent=bold, alignment=1)
        bold_right = ParagraphStyle(name="BoldRight", parent=bold, alignment=2)

        title = ParagraphStyle(
            name="Title",
            parent=bold,
            fontName=FONT_BOLD,
            fontSize=TITLE_SIZE,
            leading=TITLE_LEADING,
            alignment=0,
        )

        return {
            "base": base,
            "bold": bold,
            "italic": italic,
            "center": center,
            "right": right,
            "bold_italic": bold_italic,
            "bold_center": bold_center,
            "bold_right": bold_right,
            "title": title,
        }

    ST = _make_styles()

    # Mantém os mesmos nomes que você já usa no arquivo (compatível com seu código atual)
    st_small = ST["base"]
    st_small_b = ST["bold"]
    st_small_i = ST["italic"]
    st_small_center = ST["center"]
    st_small_right = ST["right"]
    st_small_bi = ST["bold_italic"]
    st_small_b_right = ST["bold_right"]
    st_small_b_center = ST["bold_center"]

    # Tabela inferior (rótulos/valores)
    st_lbl_r = ST["bold_right"]   # rótulo negrito alinhado à direita
    st_val_c = ST["center"]       # valor centralizado

    # Título da empresa ("USINAGEM LUMINOX")
    st_title = ST["title"]

    # --------- Dados fixos empresa ----------
    empresa_nome = "USINAGEM LUMINOX"
    empresa_sub_bold = "SERVIÇOS DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"
    empresa_end = "Rua Padre Alfredo Nesi, 582 - Guadalajara - Caucaia - CE - CEP: 61.650-280"
    empresa_cnpj = "CNPJ: 18.147.590/0001-45"
    empresa_fone = "Fone: (85) 98566-2160"
    empresa_email = "Email: usiluminox@gmail.com"

    # --------- Campos do orçamento ----------
    numero = (
        getattr(orcamento, "numero", None)
        or getattr(orcamento, "codigo", None)
        or getattr(orcamento, "id", None)
        or "-"
    )
    revisao = getattr(orcamento, "revisao", None) or getattr(orcamento, "revisao_num", None) or "-"
    data_emissao = getattr(orcamento, "criado_em", None) or getattr(orcamento, "created_at", None)
    validade = getattr(orcamento, "validade", None) or getattr(orcamento, "validade_em", None)

    elements: list[Any] = []

    page_w, page_h = fmt.page_size
    content_w = page_w - fmt.left_margin - fmt.right_margin
    content_h = page_h - fmt.top_margin - fmt.bottom_margin

    # =========================================================
    # FUNÇÃO: BORDA EXTERNA (BOX) PARA A PÁGINA INTEIRA
    # =========================================================
    def _draw_page_frame(canvas, _doc):
        """
        Desenha o retângulo externo (box) envolvendo toda a área útil do PDF.
        Isso garante que cabeçalho + conteúdo + rodapé fiquem todos dentro do mesmo contorno.
        """
        canvas.saveState()

        x = fmt.left_margin
        y = fmt.bottom_margin
        w = content_w
        h = content_h

        canvas.setLineWidth(1.2)
        canvas.setStrokeColor(theme["BLACK"])
        canvas.rect(x, y, w, h, stroke=1, fill=0)
        canvas.restoreState()

    # =========================================================
    # FUNÇÃO: RODAPÉ (ASSINATURAS) - modelo Ultragaz
    # =========================================================
    def _draw_footer_assinaturas(canvas, doc) -> None:
        """
        Assinaturas conforme modelo:
        - linha horizontal acima do nome
        - Nome: negrito + itálico (centralizado)
        - Cargo/Empresa: normal (centralizado)
        - Contratada/Contratante: itálico (centralizado)
        """
        canvas.saveState()

        # Área útil (dentro das margens)
        left = doc.leftMargin
        right = doc.pagesize[0] - doc.rightMargin
        width = right - left

        # Define 2 colunas com espaçamento central
        gap = 24 * mm
        col_w = (width - gap) / 2.0

        x_left = left
        x_right = left + col_w + gap

        # Centros das colunas
        cx_left = x_left + col_w / 2.0
        cx_right = x_right + col_w / 2.0

        # Posição vertical (ajuste fino)
        # (sobe/desce aqui se precisar encaixar no box)
        y_base = doc.bottomMargin + 1 * mm

        # Linha horizontal (acima do nome)
        line_y = y_base + 12 * mm
        line_pad = 10 * mm  # margem interna da linha na coluna

        canvas.setLineWidth(1.0)
        canvas.setStrokeColor(theme["BLACK"])
        canvas.line(x_left + line_pad, line_y, x_left + col_w - line_pad, line_y)
        canvas.line(x_right + line_pad, line_y, x_right + col_w - line_pad, line_y)

        # Textos (fontes)
        # Nome: bold + italic
        canvas.setFillColor(theme["BLACK"])
        canvas.setFont("Calibri-BoldItalic", 9)
        canvas.drawCentredString(cx_left, y_base + 9 * mm, "Fco Jackson Almeida de Oliveira")
        canvas.drawCentredString(cx_right, y_base + 9 * mm, "Suyane Gaspar")

        # Cargo/Empresa: normal
        canvas.setFont("Calibri", 9)
        canvas.drawCentredString(cx_left, y_base + 5 * mm, "Diretor Técnico - LUMINOX")
        canvas.drawCentredString(cx_right, y_base + 5 * mm, "BAIHANA DISTRIBUIDORA DE GAS LTDA")

        # Contratada/Contratante: italic
        canvas.setFont("Calibri-Italic", 9)
        canvas.drawCentredString(cx_left, y_base + 2 * mm, "Contratada")
        canvas.drawCentredString(cx_right, y_base + 2 * mm, "Contratante")

        canvas.restoreState()

    def _on_page(canvas, doc):
        _draw_page_frame(canvas, doc)
        _draw_footer_assinaturas(canvas, doc)

    # =========================================================
    # 1) CABEÇALHO - TABELA SUPERIOR (2 COLUNAS)
    # =========================================================
    logo = build_logo_image(width_mm=55.0)  # (mesmo método do padrao.py)

    # Coluna esquerda (logo + frase em negrito embaixo)
    left_cells: list[Any] = []
    if logo:
        left_cells.append(logo)
        #left_cells.append(Spacer(1, 2))
        #left_cells.append(Paragraph(escape("SERVIÇO DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"), st_small_b_center))
    else:
        # fallback caso logo não exista (não quebra)
        left_cells.append(Paragraph(escape("USINAGEM LUMINOX"), st_title))
        left_cells.append(Paragraph(escape("SERVIÇO DE TORNO, FRESA, SERRALHERIA E MANUTENÇÃO EM GERAL"), st_small_b))

    # Coluna direita (dados empresa)
    right_text = [
        Paragraph(escape(empresa_nome), st_title),
        Paragraph(escape(empresa_sub_bold), st_small_b),
        #Paragraph(escape(empresa_cnpj), st_small),
        Paragraph(escape(empresa_end), st_small),
        Paragraph(escape(f"{empresa_cnpj} - {empresa_fone} - {empresa_email}"), st_small),
    ]

    top_tbl = Table(
        [[left_cells, right_text]],
        colWidths=[60 * mm, None],  # deixa a direita “pegar o resto”
    )
    top_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                # ✅ borda externa (box) do cabeçalho superior
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                # ✅ linha vertical entre as 2 colunas (após a coluna 0)
                ("LINEAFTER", (0, 0), (0, -1), 1.0, theme["BLACK"]),

                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    # =========================================================
    # 2) CABEÇALHO - TABELA INFERIOR (4 COLUNAS / 2 LINHAS)
    # =========================================================
    bottom_tbl_data = [
        [
            Paragraph("PROPOSTA DE SERVIÇO N° :", st_lbl_r),
            Paragraph(escape(str(numero)), st_val_c),
            Paragraph("DATA DE EMISSÃO:", st_lbl_r),
            Paragraph(fmt_date(data_emissao), st_val_c),
        ],
        [
            Paragraph("REVISÃO N° :", st_lbl_r),
            Paragraph(escape(str(revisao)), st_val_c),
            Paragraph("VALIDADE DA PROPOSTA:", st_lbl_r),
            Paragraph(fmt_date(validade), st_val_c),
        ],
    ]

    bottom_tbl = Table(
        bottom_tbl_data,
        colWidths=[55 * mm, 35 * mm, 55 * mm, None],
        rowHeights=[5 * mm, 5 * mm],  # ✅ linhas mais estreitas
    )

    bottom_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                # ✅ box externo da tabela inferior
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                # Fundo cinza só nos rótulos (colunas 0 e 2)
                ("BACKGROUND", (0, 0), (0, -1), theme["LIGHT_GRAY"]),
                ("BACKGROUND", (2, 0), (2, -1), theme["LIGHT_GRAY"]),

                # ✅ alinhamentos conforme modelo
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),   # rótulos col 0 à direita
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),   # rótulos col 2 à direita
                ("ALIGN", (1, 0), (1, -1), "CENTER"),  # valores col 1 centralizados
                ("ALIGN", (3, 0), (3, -1), "CENTER"),  # valores col 3 centralizados

                # ✅ paddings menores pra “baixar” as linhas
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    # Junta as duas tabelas do cabeçalho (top + bottom) numa “stack”
    header_stack = [top_tbl, Spacer(1, 4), bottom_tbl]

    # Coloca o cabeçalho como “um bloco”
    elements.extend(header_stack)
    elements.append(Spacer(1, 4))

    # =========================================================
    # DADOS DO CLIENTE (ULTRAGAZ)
    # =========================================================

    # Puxando campos do cliente (use os nomes que já existem no seu model)
    cli_nome = getattr(cliente, "nome", None) or getattr(cliente, "name", None) or "-"
    cli_cnpj = getattr(cliente, "cnpj", None) or "-"
    cli_ie = getattr(cliente, "ie", None) or getattr(cliente, "inscricao_estadual", None) or "-"
    cli_cep = getattr(cliente, "cep", None) or "-"
    cli_endereco = getattr(cliente, "endereco", None) or "-"
    cli_bairro = getattr(cliente, "bairro", None) or "-"
    cli_cidade = getattr(cliente, "cidade", None) or "-"
    cli_estado = getattr(cliente, "estado", None) or "-"
    cli_telefone = getattr(cliente, "telefone", None) or getattr(cliente, "phone", None) or "-"
    cli_email = getattr(cliente, "email", None) or "-"

    # Estilos: rótulo (bold right) e valor (base)
    # (Você já tem st_lbl_r e st_small / st_small_b da refatoração)
    st_lbl = st_lbl_r         # bold + RIGHT
    st_val = st_small         # base

    # ---- Linha de título (span em 4 colunas) ----
    title_row = [Paragraph("DADOS DO CLIENTE", st_small_b_center), "", "", ""]

    # ---- Corpo: 2 colunas “espelhadas” ----
    # Estrutura: [label_left, value_left, label_right, value_right]
    rows = [
        title_row,
        [Paragraph("CLIENTE:", st_lbl), Paragraph(escape(str(cli_nome)), st_val),
        Paragraph("I.E:", st_lbl), Paragraph(escape(str(cli_ie)), st_val)],

        [Paragraph("CNPJ:", st_lbl), Paragraph(escape(str(cli_cnpj)), st_val),
        Paragraph("CEP:", st_lbl), Paragraph(escape(str(cli_cep)), st_val)],

        [Paragraph("ENDEREÇO:", st_lbl), Paragraph(escape(str(cli_endereco)), st_val),
        Paragraph("BAIRRO:", st_lbl), Paragraph(escape(str(cli_bairro)), st_val)],

        [Paragraph("CIDADE:", st_lbl), Paragraph(escape(str(cli_cidade)), st_val),
        Paragraph("ESTADO:", st_lbl), Paragraph(escape(str(cli_estado)), st_val)],

        [Paragraph("CONTATO:", st_lbl), Paragraph(escape(str(getattr(cliente, "contato", None) or "-")), st_val),
        Paragraph("TELEFONE:", st_lbl), Paragraph(escape(str(cli_telefone)), st_val)],

        [Paragraph("E-MAILS:", st_lbl), Paragraph(escape(str(cli_email)), st_val),
        Paragraph("E-MAILS:", st_lbl), Paragraph(escape(str(cli_email)), st_val)],
    ]

    # Larguras (total 190mm): [label, value] + [label, value]
    # Ajustadas para ficar bem parecido com o modelo
    col_widths = [28 * mm, None, 28 * mm, None]  # soma = 190mm

    tbl_cli = Table(rows, colWidths=col_widths)
    tbl_cli.setStyle(
        TableStyle(
            [
                # BOX externo
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                # Título mesclado
                ("SPAN", (0, 0), (3, 0)),
                ("BACKGROUND", (0, 0), (3, 0), theme["TITLE_BG"]),
                ("ALIGN", (0, 0), (3, 0), "CENTER"),
                ("VALIGN", (0, 0), (3, 0), "MIDDLE"),

                # Linha separando header do corpo
                ("LINEBELOW", (0, 0), (3, 0), 1.2, theme["BLACK"]),

                # ✅ Fundo cinza só nos rótulos (col 0 e col 2)
                ("BACKGROUND", (0, 1), (0, -1), theme["LIGHT_GRAY"]),
                ("BACKGROUND", (2, 1), (2, -1), theme["LIGHT_GRAY"]),

                # Alinhamentos
                ("ALIGN", (0, 1), (0, -1), "RIGHT"),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("ALIGN", (1, 1), (1, -1), "LEFT"),
                ("ALIGN", (3, 1), (3, -1), "LEFT"),

                # Padding (altura enxuta)
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    
    elements.append(tbl_cli)
    elements.append(Spacer(1, 4))

    # =========================================================
    # DESCRIÇÃO DO SERVIÇO (ULTRAGAZ)
    # =========================================================
    def _build_tbl_descricao_servico(itens: Iterable[Any]) -> Table:

        # ✅ inset para não grudar no box (2mm cada lado)
        usable_w = content_w
        usable_w_inset = usable_w - (4 * mm)

        # colunas fixas
        fixed = [10*mm, 12*mm, 28*mm, 28*mm, 28*mm]  # item, qtd, tipo, unit, total
        desc_w = usable_w_inset - sum(fixed)

        col_widths = [
            10 * mm,   # ITEM
            desc_w,    # DESCRIÇÃO (resto, com inset aplicado)
            12 * mm,   # QTD
            28 * mm,   # TIPO SERVIÇO
            28 * mm,   # VALOR UNIT.
            28 * mm,   # VALOR TOTAL
        ]
        
        def _money_cell(valor: Any, col_w_mm: float, bold: bool = False) -> Table:
            """
            Renderiza 'R$' à esquerda e valor à direita dentro da célula.
            Usa uma mini-tabela 2 colunas com widths travados para não estourar.
            """
            num = fmt_money_no_prefix(valor)

            st_rs = st_small_b if bold else st_small
            st_num = st_small_b_right if bold else st_small_right

            rs_w = 6 * mm
            cell_w = col_w_mm * mm
            num_w = max(cell_w - rs_w, 10)  # garante largura mínima

            mini = Table([[Paragraph("R$", st_rs), Paragraph(escape(num), st_num)]], colWidths=[rs_w, num_w])
            mini.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, 0), "LEFT"),
                        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            return mini
 
        def _get(obj: Any, *names: str, default: Any = "-") -> Any:
            for n in names:
                v = getattr(obj, n, None)
                if v is not None and v != "":
                    return v
            return default

        def _calc_total(item: Any) -> float:
            t = getattr(item, "total", None)
            if t is not None:
                return to_float(t)
            qtd = _get(item, "quantidade", "qtd", default=0)
            unit = _get(item, "valor_unitario", "preco_unitario", "valorUnitario", default=0)
            return to_float(qtd) * to_float(unit)

        data: list[list[Any]] = []

        # Linha 0: título
        data.append([Paragraph("DESCRIÇÃO DO SERVIÇO", st_small_b_center)] + [""] * 5)

        # Linha 1: cabeçalho
        data.append(
            [
                Paragraph("ITEM", st_small_b_center),
                Paragraph("DESCRIÇÃO DO ITEM", st_small_b_center),
                Paragraph("QTD", st_small_b_center),
                Paragraph("TIPO SERVIÇO", st_small_b_center),
                Paragraph("VALOR UNIT.", st_small_b_center),
                Paragraph("VALOR TOTAL", st_small_b_center),
            ]
        )

        # 16 linhas fixas
        itens_list = list(itens or [])
        max_rows = 16

        for i in range(max_rows):
            if i < len(itens_list):
                it = itens_list[i]
                idx = i + 1

                desc = _get(it, "descricao", "descricao_item", "nome", "item", default="-")
                tipo = _get(it, "tipo_servico", "tipo", "servico", default="TORNEARIA")
                qtd = _get(it, "quantidade", "qtd", default=0)

                unit = _get(it, "valor_unitario", "preco_unitario", "valorUnitario", default=0)
                total = _calc_total(it)

                data.append(
                    [
                        Paragraph(escape(str(idx)), st_small_center),
                        Paragraph(escape(str(desc)), st_small),
                        Paragraph(escape(fmt_number(qtd)), st_small_center),
                        Paragraph(escape(str(tipo)), st_small_center),
                        _money_cell(unit, 28),
                        _money_cell(total, 28),
                    ]
                )
            else:
                data.append([""] * 6)

        # Totais (rodapé)
        total_geral = sum_totais_itens(itens_list)
        desconto_pct = (
            getattr(orcamento, "desconto_percent", None)
            or getattr(orcamento, "desconto_pct", None)
            or getattr(orcamento, "desconto", None)
            or 0
        )
        desconto_pct = to_float(desconto_pct)
        total_com_desc = total_geral * (1.0 - (desconto_pct / 100.0))

        # Linha: TOTAL GERAL DO SERVIÇO
        data.append(
            [
                Paragraph("TOTAL GERAL DO SERVIÇO:", st_lbl_r),
                "", "", "",
                _money_cell(total_geral, 54, bold=True),
                "",
            ]
        )

        # Linha: TOTAL COM DESCONTO DE (0%)
        data.append(
            [
                Paragraph(f"TOTAL COM DESCONTO DE {fmt_number(desconto_pct)}%:", st_lbl_r),
                "", "", "",
                _money_cell(total_com_desc, 54, bold=True),
                "",
            ]
        )

        tbl = Table(data, colWidths=col_widths)

        first_item_row = 2
        last_item_row = first_item_row + (max_rows - 1)
        total_row_1 = last_item_row + 1
        total_row_2 = last_item_row + 2

        tbl.setStyle(
            TableStyle(
                [
                    # Bordas fortes
                    ("GRID", (0, 0), (-1, -1), 1.0, theme["GRID"]),
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                    ("LINEBELOW", (0, 0), (-1, 0), 1.2, theme["BLACK"]),

                    # Título
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), theme["TITLE_BG"]),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),

                    # Cabeçalho
                    ("BACKGROUND", (0, 1), (-1, 1), theme["LIGHT_BLUE"]),
                    ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                    ("VALIGN", (0, 1), (-1, 1), "MIDDLE"),

                    # QTD azul (somente corpo)
                    ("BACKGROUND", (2, first_item_row), (2, last_item_row), theme["LIGHT_BLUE"]),

                    # Totais: spans conforme solicitado
                    ("SPAN", (0, total_row_1), (3, total_row_1)),  # texto 0..3
                    ("SPAN", (4, total_row_1), (5, total_row_1)),  # valor 4..5
                    ("SPAN", (0, total_row_2), (3, total_row_2)),
                    ("SPAN", (4, total_row_2), (5, total_row_2)),

                    # Totais: alinhamento e fundo (modelo)
                    ("ALIGN", (0, total_row_1), (3, total_row_2), "RIGHT"),
                    ("ALIGN", (4, total_row_1), (5, total_row_2), "RIGHT"),
                    ("VALIGN", (0, first_item_row), (-1, total_row_2), "MIDDLE"),
                    ("BACKGROUND", (0, total_row_1), (3, total_row_2), theme["TITLE_BG"]),
                    ("BACKGROUND", (4, total_row_1), (5, total_row_2), theme["LIGHT_GRAY"]),

                    # Linhas mais baixas (paddings menores)
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    
                    # Borda inferior na cor preta na linha 16
                    ("LINEBELOW", (0, last_item_row), (-1, last_item_row), 1.2, theme["BLACK"]),
                ]
            )
        )

        return tbl

    # =========================================================
    # DESCRITIVO (ULTRAGAZ) - vem de orcamento.observacoes
    # =========================================================
    def _build_tbl_descritivo() -> Table:
        usable_w_inset = content_w - (4 * mm)  # inset 2mm cada lado

        obs = (
            getattr(orcamento, "observacoes", None)
            or getattr(orcamento, "observacao", None)
            or getattr(orcamento, "obs", None)
            or ""
        )
        obs = str(obs or "").strip()

        data = [
            [Paragraph("DESCRITIVO", st_small_b_center)],
            [Paragraph(escape(obs) if obs else "&nbsp;", st_small)],
        ]

        tbl = Table(data, colWidths=[usable_w_inset], rowHeights=[5 * mm, 18 * mm])
        tbl.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                    ("BACKGROUND", (0, 0), (-1, 0), theme["TITLE_BG"]),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1.2, theme["BLACK"]),

                    ("VALIGN", (0, 1), (-1, 1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        return tbl

    # =========================================================
    # PRAZOS E CONDIÇÕES DE PAGAMENTO (ULTRAGAZ)
    # =========================================================
    def _build_tbl_prazos_pagamento() -> Table:
        usable_w_inset = content_w - (4 * mm)  # inset 2mm cada lado

        # Defaults por enquanto (até entrar no formulário)
        prazo_exec_dias = (
            getattr(orcamento, "prazo_execucao_dias", None)
            or getattr(orcamento, "prazo_execucao", None)
            or 30
        )
        cond_pag_dias = (
            getattr(orcamento, "condicao_pagamento_dias", None)
            or getattr(orcamento, "condicao_pagamento", None)
            or 30
        )

        prazo_exec_dias = int(to_float(prazo_exec_dias) or 30)
        cond_pag_dias = int(to_float(cond_pag_dias) or 30)

        # Texto (sem itálico)
        txt_prazo = f"{prazo_exec_dias} dias, após a aprovação da proposta, a contar do recebimento do material."
        txt_coleta = "Coleta e entrega inclusos na proposta. Dispensamos assinaturas na proposta, se enviado por e-mail."
        txt_pagto = f"{cond_pag_dias} dias, através de transferência bancária."

        # 2 colunas (rótulo | texto)
        # Ajuste de largura para ficar parecido com o modelo
        col_label = 38 * mm
        col_text = usable_w_inset - col_label

        data = [
            # Linha 0: título (span)
            [Paragraph("PRAZOS E CONDIÇÕES DE PAGAMENTO", st_small_b_center), ""],

            # Linhas 1..3: 2 colunas, 3 linhas (sem grid)
            [Paragraph("Prazo de execução:", st_small_bi), Paragraph(escape(txt_prazo), st_small_i)],
            [Paragraph("Condição de pagamento:", st_small_bi), Paragraph(escape(txt_pagto), st_small_i)],
            ["", Paragraph(escape(txt_coleta), st_small_i)],
        ]

        tbl = Table(
            data,
            colWidths=[col_label, col_text],
            rowHeights=[5 * mm, None, None, None],  # título fixo, restante automático
        )

        tbl.setStyle(
            TableStyle(
                [
                    # Borda externa (sem GRID interno)
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                    # Título
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), theme["TITLE_BG"]),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1.2, theme["BLACK"]),

                    # Conteúdo (linhas 1..3)
                    ("BACKGROUND", (0, 1), (0, -1), theme["LIGHT_GRAY"]),
                    ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),

                    # Alinhamento
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "LEFT"),
                ]
            )
        )

        return tbl

    # ✅ adiciona a tabela no fluxo do PDF
    tbl_desc = _build_tbl_descricao_servico(itens)
    elements.append(tbl_desc)
    elements.append(Spacer(1, 4))

    elements.append(_build_tbl_descritivo())
    elements.append(Spacer(1, 4))
    
    elements.append(_build_tbl_prazos_pagamento())

    # Build com frame externo em todas as páginas
    doc.build(elements, onFirstPage=_on_page, onLaterPages=_on_page)

    return buf.getvalue()
