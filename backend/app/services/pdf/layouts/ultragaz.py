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

    if os.path.exists(calibri):
        pdfmetrics.registerFont(TTFont("Calibri", calibri))
    if os.path.exists(calibri_b):
        pdfmetrics.registerFont(TTFont("Calibri-Bold", calibri_b))

_register_calibri()

# print("Fonts registradas:", "Calibri" in pdfmetrics.getRegisteredFontNames(), "Calibri-Bold" in pdfmetrics.getRegisteredFontNames())

def render_pdf_ultragaz(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout ULTRAGAZ (conforme modelo do cliente).
    - Usa helpers/styles/assets compartilhados (mesmo padrão do padrao.py)
    - Cabeçalho com 2 tabelas (topo 2 colunas + faixa 4 colunas/2 linhas)
    - Box externo em volta da página inteira (área útil)
    """
    buf = BytesIO()
    fmt = PDF_FORMAT_ULTRAGAZ

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

    BASE_SIZE = 9          # ✅ base do layout Ultragaz
    BASE_LEADING = 13      # ✅ entrelinhas confortável p/ 9

    TITLE_SIZE = 16        # ✅ "USINAGEM LUMINOX" maior
    TITLE_LEADING = 20

    def _make_styles():
        base = ParagraphStyle(
            name="Base",
            parent=styles["Normal"],
            fontName=FONT,
            fontSize=BASE_SIZE,
            leading=BASE_LEADING,
        )
        bold = ParagraphStyle(name="Bold", parent=base, fontName=FONT_BOLD)

        center = ParagraphStyle(name="Center", parent=base, alignment=1)  # CENTER
        right = ParagraphStyle(name="Right", parent=base, alignment=2)    # RIGHT

        bold_center = ParagraphStyle(name="BoldCenter", parent=bold, alignment=1)
        bold_right = ParagraphStyle(name="BoldRight", parent=bold, alignment=2)

        title = ParagraphStyle(
            name="Title",
            parent=bold,
            fontName=FONT_BOLD,
            fontSize=TITLE_SIZE,
            leading=TITLE_LEADING,
            alignment=0,  # LEFT
        )

        return {
            "base": base,
            "bold": bold,
            "center": center,
            "right": right,
            "bold_center": bold_center,
            "bold_right": bold_right,
            "title": title,
        }

    ST = _make_styles()

    # Mantém os mesmos nomes que você já usa no arquivo (compatível com seu código atual)
    st_small = ST["base"]
    st_small_b = ST["bold"]
    st_small_center = ST["center"]
    st_small_right = ST["right"]
    st_small_b_center = ST["bold_center"]

    # Tabela inferior (rótulos/valores)
    st_lbl_r = ST["bold_right"]   # rótulo negrito alinhado à direita
    st_val_c = ST["center"]       # valor centralizado

    # Título da empresa ("USINAGEM LUMINOX")
    st_title = ST["title"]

    # Cores (ajustáveis)
    grey_label = colors.HexColor("#EFEFEF")  # fundo cinza claro rótulos
    grey_grid = colors.HexColor("#A0A0A0")   # linhas internas
    black = colors.black

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

    # --------- Cliente (se precisar depois) ----------
    cli_nome = getattr(cliente, "nome", None) or getattr(cliente, "name", None) or "-"

    elements: list[Any] = []

    # =========================================================
    # FUNÇÃO: BORDA EXTERNA (BOX) PARA A PÁGINA INTEIRA
    # =========================================================
    def _draw_page_frame(canvas, _doc):
        """
        Desenha o retângulo externo (box) envolvendo toda a área útil do PDF.
        Isso garante que cabeçalho + conteúdo + rodapé fiquem todos dentro do mesmo contorno.
        """
        canvas.saveState()
        page_w, page_h = fmt.page_size

        x = fmt.left_margin
        y = fmt.bottom_margin
        w = page_w - fmt.left_margin - fmt.right_margin
        h = page_h - fmt.top_margin - fmt.bottom_margin

        canvas.setLineWidth(1.2)
        canvas.setStrokeColor(black)
        canvas.rect(x, y, w, h, stroke=1, fill=0)
        canvas.restoreState()

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
                ("BOX", (0, 0), (-1, -1), 1.2, colors.black),

                # ✅ linha vertical entre as 2 colunas (após a coluna 0)
                ("LINEAFTER", (0, 0), (0, -1), 1.0, colors.black),

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
                ("BOX", (0, 0), (-1, -1), 1.2, colors.black),

                # ✅ sem grid interno
                # (não usar INNERGRID / GRID)

                # Fundo cinza só nos rótulos (colunas 0 e 2)
                ("BACKGROUND", (0, 0), (0, -1), grey_label),
                ("BACKGROUND", (2, 0), (2, -1), grey_label),

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
    # se existir lista de emails no seu banco, ajustamos depois

    # Cores (reaproveite as mesmas do arquivo)
    bg_header = colors.HexColor("#D9D9D9")   # faixa do título
    bg_body = colors.HexColor("#EEEEEE")     # fundo do corpo

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
                ("BOX", (0, 0), (-1, -1), 1.2, colors.black),

                # Título mesclado
                ("SPAN", (0, 0), (3, 0)),
                ("BACKGROUND", (0, 0), (3, 0), bg_header),
                ("ALIGN", (0, 0), (3, 0), "CENTER"),
                ("VALIGN", (0, 0), (3, 0), "MIDDLE"),

                # Linha separando header do corpo
                ("LINEBELOW", (0, 0), (3, 0), 1.2, colors.black),

                # ✅ Fundo do corpo: valores brancos
                ("BACKGROUND", (0, 1), (3, -1), colors.white),

                # ✅ Fundo cinza só nos rótulos (col 0 e col 2)
                ("BACKGROUND", (0, 1), (0, -1), bg_body),
                ("BACKGROUND", (2, 1), (2, -1), bg_body),

                # Divisor vertical central (entre col 1 e col 2)
                #("LINEAFTER", (1, 1), (1, -1), 1.2, colors.black),

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
    elements.append(Spacer(1, 8))

    # Build com frame externo em todas as páginas
    doc.build(elements, onFirstPage=_draw_page_frame, onLaterPages=_draw_page_frame)

    return buf.getvalue()
