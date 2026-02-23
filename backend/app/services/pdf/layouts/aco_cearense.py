from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable
import os

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..shared.helpers import (
    escape,
    fmt_date,
    fmt_money_no_prefix,
    fmt_number,
    sum_totais_itens,
    to_float,
)
from ..shared.styles import PDF_FORMAT_ACO_CEARENSE


# =========================================================
# FONTES (mesmo padrão do ultragaz.py)
# =========================================================
def _register_calibri() -> None:
    """
    Registra Calibri/Calibri Bold/Italic/BoldItalic.
    Mantém fallback automático se os arquivos não existirem (não quebra PDF).
    """
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


# =========================================================
# ASSET: logo específica do layout (sem mexer no shared.assets)
# =========================================================
def _build_aco_logo_image(width_mm: float = 40.0) -> Image | None:
    """
    Cria um Image (ReportLab) com largura em mm e altura proporcional,
    usando a logo do cliente Aço Cearense que fica na MESMA pasta do layout.

    Arquivo esperado:
    backend/app/services/pdf/layouts/logo_grupo_aco_cearense.png

    Retorna None se não existir (não quebra o PDF).
    """
    logo_path = os.path.join(os.path.dirname(__file__), "logo_grupo_aco_cearense.png")
    if not os.path.exists(logo_path):
        return None

    # Mantém proporção usando ImageReader (mesmo método do shared.assets)
    ir = ImageReader(str(logo_path))
    px_w, px_h = ir.getSize()

    w = width_mm * mm
    h = w * (px_h / float(px_w))

    img = Image(str(logo_path), width=w, height=h)
    img.hAlign = "LEFT"
    return img


def render_pdf_aco_cearense(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout AÇO CEARENSE (conforme modelo "Anexo V - Formulário de Orçamento").

    Objetivo desta etapa:
    - implementar o layout usando o MESMO padrão de estrutura do ultragaz.py:
      theme centralizado, registro de fontes centralizado, helpers/shared, estilos no topo.
    - manter linhas fixas nas tabelas (serviço e material)
    """
    buf = BytesIO()
    fmt = PDF_FORMAT_ACO_CEARENSE

    doc = SimpleDocTemplate(
        buf,
        pagesize=fmt.page_size,
        leftMargin=fmt.left_margin,
        rightMargin=fmt.right_margin,
        topMargin=fmt.top_margin,
        bottomMargin=fmt.bottom_margin,
        title="Orçamento/Medição - Aço Cearense",
        author="Usinagem Luminox",
    )

    # =========================================================
    # TEMA / CORES (mesmo estilo do ultragaz.py)
    # =========================================================
    theme = {
        "BLACK": colors.black,
        "WHITE": colors.white,
        "GRID": colors.black,  # no modelo, o grid é bem preto
        "TITLE_BLUE": colors.HexColor("#002060"),  # cor dos títulos (cliente)
    }

    styles = getSampleStyleSheet()

    # =========================================================
    # STYLES (centralizados no topo)
    # =========================================================
    FONT = "Calibri"
    FONT_B = "Calibri-Bold"

    st_base = ParagraphStyle(
        name="Base",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=9,
        leading=11,
        textColor=theme["BLACK"],
    )
    st_base_c = ParagraphStyle(name="BaseC", parent=st_base, alignment=1)
    st_base_r = ParagraphStyle(name="BaseR", parent=st_base, alignment=2)

    st_small = ParagraphStyle(
        name="Small",
        parent=st_base,
        fontSize=9,
        leading=10.5,
    )
    st_small_c = ParagraphStyle(name="SmallC", parent=st_small, alignment=1)
    st_small_r = ParagraphStyle(name="SmallR", parent=st_small, alignment=2)

    st_bold = ParagraphStyle(name="Bold", parent=st_base, fontName=FONT_B)
    st_bold_c = ParagraphStyle(name="BoldC", parent=st_bold, alignment=1)
    st_bold_r = ParagraphStyle(name="BoldR", parent=st_bold, alignment=2)

    st_title_top = ParagraphStyle(
        name="TitleTop",
        parent=st_bold_c,
        fontSize=11,
        leading=13,
    )

    # Texto branco usado nas faixas azuis
    st_bar_white = ParagraphStyle(
        name="BarWhite",
        parent=st_bold_c,
        fontSize=9,
        leading=12,
        textColor=theme["WHITE"],
    )

    # =========================================================
    # Helpers internos (seguem padrão simples, sem dependências extras)
    # =========================================================
    def _get(obj: Any, *names: str, default: Any = "-") -> Any:
        """
        Busca o primeiro atributo existente em `obj` na lista `names`.
        Evita ifs repetidos e mantém o layout tolerante a pequenas variações de schema.
        """
        for n in names:
            v = getattr(obj, n, None)
            if v is not None and v != "":
                return v
        return default

    def _money_cell(valor: Any) -> Table:
        """
        Célula estilo "R$ | valor" com alinhamento do valor à direita.
        (Mantém a apresentação do modelo)
        """
        num = fmt_money_no_prefix(valor)
        t = Table(
            [[Paragraph("R$", st_small), Paragraph(escape(num), st_small_r)]],
            colWidths=[7 * mm, None],
        )
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return t

    # =========================================================
    # DADOS DO FORMULÁRIO
    # =========================================================
    numero = _get(orcamento, "numero", "codigo", "id", default="-")
    data_emissao = _get(orcamento, "criado_em", "created_at", default=None)
    data_emissao_txt = fmt_date(data_emissao)

    cli_nome = _get(cliente, "nome", "name", default="AÇO CEARENSE")
    contato_fornecedor = _get(orcamento, "contato_fornecedor", "contato", default="-")
    solicitante = _get(orcamento, "solicitante", "solicitante_nome", default="-")

    prazo_entrega_dias = _get(orcamento, "prazo_entrega_dias", "prazo_entrega", "prazo_execucao_dias", default=10)
    try:
        prazo_entrega_dias = int(to_float(prazo_entrega_dias) or 10)
    except Exception:
        prazo_entrega_dias = 10

    necessario_desenho = _get(orcamento, "necessario_desenho", "precisa_desenho", default=None)
    if necessario_desenho in (True, 1, "1", "true", "True", "SIM", "Sim", "sim"):
        desenho_txt = "Sim ( X )        Não (   )"
    elif necessario_desenho in (False, 0, "0", "false", "False", "NAO", "Não", "nao", "não"):
        desenho_txt = "Sim (   )        Não ( X )"
    else:
        desenho_txt = "Sim (   )        Não (   )"

    # Texto grande central do formulário (no modelo é um campo grande)
    desc_grande = str(_get(orcamento, "observacoes", "observacao", "descricao", "descricao_servico", default="")).strip()

    itens_list = list(itens or [])

    # =========================================================
    # Heurística simples para separar Serviço vs Material
    # (podemos ajustar depois quando vocês definirem regra oficial)
    # =========================================================
    def _is_material(it: Any) -> bool:
        tipo = str(_get(it, "tipo_servico", "tipo", "categoria", default="")).upper()
        unidade = str(_get(it, "unidade", "unidade_sigla", "unidade_medida", default="")).lower()

        if "MATER" in tipo:
            return True
        if unidade in ("kg", "quilo", "quilos"):
            return True
        return False

    itens_serv = [i for i in itens_list if not _is_material(i)]
    itens_mat = [i for i in itens_list if _is_material(i)]

    # =========================================================
    # LARGURA ÚTIL (para tabelas)
    # =========================================================
    content_w = fmt.page_size[0] - fmt.left_margin - fmt.right_margin

    # =========================================================
    # 1) TÍTULO SUPERIOR
    # =========================================================
    elements: list[Any] = []
    elements.append(Paragraph("Anexo V - Formulário de Orçamento", st_title_top))
    elements.append(Spacer(1, 4))

    # =========================================================
    # 2) CABEÇALHO (logo + título)
    # =========================================================
    logo = _build_aco_logo_image(40.0)
    title_form = Paragraph("Orçamento/Medição de Serviço de Usinagem", st_bold_c)

    top_header = Table(
        [[logo if logo else "", title_form]],
        colWidths=[55 * mm, content_w - (55 * mm)],
        rowHeights=[10 * mm],
    )
    top_header.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elements.append(top_header)

    # =========================================================
    # 3) GRADE DE CAMPOS (conforme modelo)
    # =========================================================
    grid_cols = [25 * mm, 85 * mm, 22 * mm, content_w - (25 + 85 + 22) * mm]
    header_grid = Table(
        [
            [
                Paragraph("Fornecedor:", st_small),
                Paragraph("USINAGEM LUMINOX", st_bold),
                Paragraph("N. Orç:", st_small),
                Paragraph(f"{escape(str(numero))}            {escape(data_emissao_txt)}", st_small),
            ],
            [
                Paragraph("Cliente:", st_small),
                Paragraph(escape(str(cli_nome)), st_bold),
                Paragraph("Necessário Desenho?", st_small),
                Paragraph(escape(desenho_txt), st_small),
            ],
            [
                Paragraph("Contato Fornecedor:", st_small),
                Paragraph(escape(str(contato_fornecedor)), st_bold),
                Paragraph("", st_small),
                Paragraph("", st_small),
            ],
            [
                Paragraph("Solicitante:", st_small),
                Paragraph(escape(str(solicitante)), st_bold),
                Paragraph("Prazo de Entrega (em dias):", st_small),
                Paragraph(escape(f"{prazo_entrega_dias} dias"), st_bold),
            ],
        ],
        colWidths=grid_cols,
        rowHeights=[5 * mm, 5 * mm, 5 * mm, 5 * mm],
    )
    header_grid.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1.0, theme["GRID"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    elements.append(header_grid)

    # =========================================================
    # 4) CAIXA GRANDE DE DESCRIÇÃO
    # =========================================================
    desc_tbl = Table(
        [[Paragraph(escape(desc_grande) if desc_grande else "&nbsp;", st_small)]],
        colWidths=[content_w],
        rowHeights=[62 * mm],
    )
    desc_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.0, theme["BLACK"]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    elements.append(desc_tbl)

    # =========================================================
    # 5) TABELA SERVIÇOS (Homem Hora / Maquina) - 10 linhas fixas
    # =========================================================
    def _build_tbl_servicos() -> Table:
        col_w = [20 * mm, 75 * mm, 25 * mm, 22 * mm, content_w - (20 + 75 + 25 + 22) * mm]

        data: list[list[Any]] = []
        data.append([Paragraph("Homem Hora / Maquina", st_bar_white), "", "", "", ""])
        data.append(
            [
                Paragraph("Item", st_bar_white),
                Paragraph("Operação", st_bar_white),
                Paragraph("Qtd Horas", st_bar_white),
                Paragraph("Vlr Unit", st_bar_white),
                Paragraph("Vlr Total", st_bar_white),
            ]
        )

        max_rows = 10
        for idx in range(max_rows):
            if idx < len(itens_serv):
                it = itens_serv[idx]
                item_no = f"{idx + 1:02d}"

                operacao = _get(it, "descricao", "descricao_item", "nome", default="-")
                qtd = _get(it, "quantidade", "qtd", default=0)
                unit = _get(it, "valor_unitario", "preco_unitario", "valorUnitario", default=0)

                total = getattr(it, "total", None)
                if total is None:
                    total = to_float(qtd) * to_float(unit)

                data.append(
                    [
                        Paragraph(escape(item_no), st_base_c),
                        Paragraph(escape(str(operacao)), st_small),
                        Paragraph(escape(fmt_number(qtd)), st_base_c),
                        _money_cell(unit),
                        _money_cell(total),
                    ]
                )
            else:
                data.append(["", "", "", "", ""])

        t = Table(data, colWidths=col_w, rowHeights=[5 * mm, 5 * mm] + [5 * mm] * max_rows)
        t.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 1), theme["TITLE_BLUE"]),
                    ("TEXTCOLOR", (0, 0), (-1, 1), theme["WHITE"]),
                    ("ALIGN", (0, 0), (-1, 1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    ("GRID", (0, 1), (-1, -1), 1.0, theme["GRID"]),
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return t

    elements.append(_build_tbl_servicos())
    elements.append(Spacer(1, 3))

    # =========================================================
    # 6) TABELA MATERIAIS (Matéria-Prima) - 8 linhas fixas
    # =========================================================
    def _build_tbl_materiais() -> Table:
        col_w = [20 * mm, 75 * mm, 25 * mm, 22 * mm, content_w - (20 + 75 + 25 + 22) * mm]

        data: list[list[Any]] = []
        data.append([Paragraph("Material ( Matéria-Prima)", st_bar_white), "", "", "", ""])
        data.append(
            [
                Paragraph("Item", st_bar_white),
                Paragraph("Descrição", st_bar_white),
                Paragraph("Qtd kg", st_bar_white),
                Paragraph("Vlr Unit", st_bar_white),
                Paragraph("Vlr Total", st_bar_white),
            ]
        )

        max_rows = 8
        for idx in range(max_rows):
            if idx < len(itens_mat):
                it = itens_mat[idx]
                item_no = f"{idx + 1:02d}"

                desc = _get(it, "descricao", "descricao_item", "nome", default="-")
                qtd = _get(it, "quantidade", "qtd", default=0)
                unit = _get(it, "valor_unitario", "preco_unitario", "valorUnitario", default=0)

                total = getattr(it, "total", None)
                if total is None:
                    total = to_float(qtd) * to_float(unit)

                data.append(
                    [
                        Paragraph(escape(item_no), st_base_c),
                        Paragraph(escape(str(desc)), st_small),
                        Paragraph(escape(fmt_number(qtd)), st_base_c),
                        _money_cell(unit),
                        _money_cell(total),
                    ]
                )
            else:
                data.append(["", "", "", "", ""])

        t = Table(data, colWidths=col_w, rowHeights=[5 * mm, 5 * mm] + [5 * mm] * max_rows)
        t.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 1), theme["TITLE_BLUE"]),
                    ("TEXTCOLOR", (0, 0), (-1, 1), theme["WHITE"]),
                    ("ALIGN", (0, 0), (-1, 1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    ("GRID", (0, 1), (-1, -1), 1.0, theme["GRID"]),
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return t

    elements.append(_build_tbl_materiais())

    # =========================================================
    # 7) TOTAL
    # =========================================================
    total_geral = sum_totais_itens(itens_list)

    total_tbl = Table(
        [
            [
                Paragraph("Valor Total do Orçamento", st_bar_white),
                Paragraph("R$", st_bold),
                Paragraph(escape(fmt_money_no_prefix(total_geral)), st_bold_r),
            ]
        ],
        colWidths=[content_w - 45 * mm, 10 * mm, 35 * mm],
        rowHeights=[8 * mm],
    )
    total_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), theme["TITLE_BLUE"]),
                ("TEXTCOLOR", (0, 0), (0, 0), theme["WHITE"]),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                ("GRID", (0, 0), (-1, -1), 1.0, theme["GRID"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(total_tbl)

    # =========================================================
    # 8) APROVAÇÃO + ASSINATURAS
    # =========================================================
    aprov_bar = Table(
        [[Paragraph("Aprovação do Orçamento", st_bar_white)]],
        colWidths=[content_w],
        rowHeights=[8 * mm],
    )
    aprov_bar.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), theme["TITLE_BLUE"]),
                ("TEXTCOLOR", (0, 0), (-1, -1), theme["WHITE"]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
            ]
        )
    )
    elements.append(aprov_bar)

    sign_tbl = Table(
        [
            ["", "", ""],
            [
                Paragraph("________________________________", st_base_c),
                Paragraph("________________________________", st_base_c),
                Paragraph("________________________________", st_base_c),
            ],
            [
                Paragraph("Solicitante da Aço\nCearense", st_base_c),
                Paragraph("Responsável\nTécnico da Aço\nCearense", st_base_c),
                Paragraph("Responsável da\nCONTRATADA", st_base_c),
            ],
        ],
        colWidths=[content_w / 3.0] * 3,
        rowHeights=[14 * mm, 8 * mm, 12 * mm],
    )
    sign_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elements.append(sign_tbl)

    # Build final
    doc.build(elements)
    return buf.getvalue()