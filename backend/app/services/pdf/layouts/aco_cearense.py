from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..shared.helpers import (
    escape,
    fmt_date,
    fmt_number,
    fmt_money_no_prefix,
    sum_totais_itens,
    to_float,
)

# Se vocês já tiverem um formato próprio no shared.styles no futuro,
# é só trocar aqui. Por enquanto, usamos A4 e margens seguras.
# (não mexe no PADRÃO e não depende de constante nova)
_DEFAULT_PAGE_SIZE = A4
_DEFAULT_MARGINS = {
    "left": 10 * mm,
    "right": 10 * mm,
    "top": 10 * mm,
    "bottom": 10 * mm,
}


def _register_calibri() -> None:
    """
    Registra Calibri/Calibri Bold/Italic/BoldItalic (mesmo padrão do ultragaz.py).
    Mantém fallback automático se os arquivos não existirem.
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


def _build_logo_aco_cearense(width_mm: float = 40.0) -> Image | None:
    """
    Carrega a logo do Grupo Aço Cearense a partir da mesma pasta do layout:
    backend/app/services/pdf/layouts/logo_grupo_aco_cearense.png

    Se não existir, retorna None (sem quebrar o PDF).
    """
    here = os.path.dirname(__file__)
    logo_path = os.path.join(here, "logo_grupo_aco_cearense.png")
    if not os.path.exists(logo_path):
        return None

    try:
        reader = ImageReader(logo_path)
        iw, ih = reader.getSize()
        w = width_mm * mm
        h = (w * ih) / float(iw)
        img = Image(logo_path, width=w, height=h)
        return img
    except Exception:
        return None


def render_pdf_aco_cearense(orcamento: Any, itens: Iterable[Any], cliente: Any) -> bytes:
    """
    Layout AÇO CEARENSE (conforme modelo "Anexo V - Formulário de Orçamento").

    Estrutura:
    - Título superior centralizado
    - Box principal com borda
      - Linha 1: logo (esq) + título do formulário (dir)
      - Cabeçalho com campos (Fornecedor, Cliente, Contatos, etc.)
      - Área grande de descrição (texto vindo do orçamento)
      - Tabela "Homem Hora / Maquina" (10 linhas)
      - Tabela "Material ( Matéria-Prima)" (8 linhas)
      - Faixa "Valor Total do Orçamento" + total
      - Faixa "Aprovação do Orçamento" + 3 assinaturas
    """
    buf = BytesIO()

    # =========================
    # TEMA (CORES E FONTES)
    # =========================
    theme = {
        "BLACK": colors.black,
        "WHITE": colors.white,
        "BLUE": colors.HexColor("#002060"),  # títulos/faixas
        "GRID": colors.black,                # no modelo, linhas bem “pretas”
    }

    # =========================
    # DOC
    # =========================
    doc = SimpleDocTemplate(
        buf,
        pagesize=_DEFAULT_PAGE_SIZE,
        leftMargin=_DEFAULT_MARGINS["left"],
        rightMargin=_DEFAULT_MARGINS["right"],
        topMargin=_DEFAULT_MARGINS["top"],
        bottomMargin=_DEFAULT_MARGINS["bottom"],
        title="Orçamento - Aço Cearense",
        author="Usinagem Luminox",
    )

    styles = getSampleStyleSheet()

    # =========================
    # STYLES CENTRALIZADOS
    # =========================
    FONT = "Calibri"
    FONT_B = "Calibri-Bold"
    FONT_I = "Calibri-Italic"
    FONT_BI = "Calibri-BoldItalic"

    BASE = ParagraphStyle(
        name="Base",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=9,
        leading=11,
        textColor=theme["BLACK"],
    )
    BASE_C = ParagraphStyle(name="BaseC", parent=BASE, alignment=1)
    BASE_R = ParagraphStyle(name="BaseR", parent=BASE, alignment=2)

    BOLD = ParagraphStyle(name="Bold", parent=BASE, fontName=FONT_B)
    BOLD_C = ParagraphStyle(name="BoldC", parent=BOLD, alignment=1)
    BOLD_R = ParagraphStyle(name="BoldR", parent=BOLD, alignment=2)

    SMALL = ParagraphStyle(name="Small", parent=BASE, fontSize=8.5, leading=10.5)
    SMALL_C = ParagraphStyle(name="SmallC", parent=SMALL, alignment=1)
    SMALL_R = ParagraphStyle(name="SmallR", parent=SMALL, alignment=2)
    SMALL_B = ParagraphStyle(name="SmallB", parent=SMALL, fontName=FONT_B)

    TITLE_TOP = ParagraphStyle(
        name="TitleTop",
        parent=BOLD_C,
        fontSize=11,
        leading=13,
    )

    BAR_WHITE = ParagraphStyle(
        name="BarWhite",
        parent=BOLD_C,
        fontSize=10,
        leading=12,
        textColor=theme["WHITE"],
    )

    # =========================
    # HELPERS (campos)
    # =========================
    def _get(obj: Any, *names: str, default: Any = "-") -> Any:
        for n in names:
            v = getattr(obj, n, None)
            if v is not None and v != "":
                return v
        return default

    def _money_cell(valor: Any, bold: bool = False) -> Table:
        """
        Célula estilo modelo: 'R$' à esquerda e valor à direita.
        """
        num = fmt_money_no_prefix(valor)
        st_rs = SMALL_B if bold else SMALL
        st_num = SMALL_B if bold else SMALL
        st_num_r = ParagraphStyle("NumR", parent=st_num, alignment=2)

        rs_w = 7 * mm
        # largura do valor se ajusta “no automático” pela tabela pai; aqui só formatamos alinhamentos
        t = Table([[Paragraph("R$", st_rs), Paragraph(escape(num), st_num_r)]], colWidths=[rs_w, None])
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

    # =========================
    # DADOS PRINCIPAIS (modelo)
    # =========================
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
    # Se não vier nada do banco, mantém em branco (ninguém marcado)
    if necessario_desenho in (True, 1, "1", "true", "True", "SIM", "Sim", "sim"):
        desenho_txt = "Sim ( X )        Não (   )"
    elif necessario_desenho in (False, 0, "0", "false", "False", "NAO", "Não", "nao", "não"):
        desenho_txt = "Sim (   )        Não ( X )"
    else:
        desenho_txt = "Sim (   )        Não (   )"

    # Descrição grande (usa observações; fallback para campos alternativos)
    desc_grande = (
        str(_get(orcamento, "observacoes", "observacao", "descricao", "descricao_servico", default="")).strip()
    )

    # =========================
    # SPLIT ITENS: SERVIÇO x MATERIAL (heurística)
    # =========================
    itens_list = list(itens or [])

    def _is_material(it: Any) -> bool:
        tipo = str(_get(it, "tipo_servico", "tipo", "categoria", default="")).upper()
        un = str(_get(it, "unidade", "unidade_sigla", "unidade_medida", default="")).lower()
        if "MATER" in tipo:
            return True
        if un in ("kg", "quilo", "quilos"):
            return True
        return False

    itens_serv = [i for i in itens_list if not _is_material(i)]
    itens_mat = [i for i in itens_list if _is_material(i)]

    # =========================
    # COMPONENTES (tabelas)
    # =========================
    content_w = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

    # --- Linha topo do box: logo + título do formulário ---
    logo = _build_logo_aco_cearense(40.0)
    title_form = Paragraph("Orçamento/Medição de Serviço de Usinagem", BOLD_C)

    top_header = Table(
        [[logo if logo else "", title_form]],
        colWidths=[55 * mm, content_w - (55 * mm)],
        rowHeights=[14 * mm],
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

    # --- Grade de campos (Fornecedor/Cliente/Contato/Solicitante/Orçamento/Data etc) ---
    # 2 blocos horizontais: esquerda (labels/valores) e direita (N. Orç / Data / etc)
    # Layout do modelo:
    # Fornecedor | USINAGEM LUMINOX || N. Orç: 002/26 | 10/02/2026
    # Cliente    | ACO CEARENSE     || Necessário desenho? | Sim... Não...
    # Contato... | JACKSON          || (vazio/mesmo campo do desenho)
    # Solicit... | CASSIA ...       || Prazo entrega ...: 10 dias
    grid_cols = [25 * mm, 85 * mm, 22 * mm, content_w - (25 + 85 + 22) * mm]
    header_grid = Table(
        [
            [Paragraph("Fornecedor:", SMALL), Paragraph("USINAGEM LUMINOX", SMALL_B),
             Paragraph("N. Orç:", SMALL), Paragraph(f"{escape(str(numero))}            {escape(data_emissao_txt)}", SMALL)],
            [Paragraph("Cliente:", SMALL), Paragraph(escape(str(cli_nome)), SMALL_B),
             Paragraph("Necessário Desenho?", SMALL), Paragraph(escape(desenho_txt), SMALL)],
            [Paragraph("Contato Fornecedor:", SMALL), Paragraph(escape(str(contato_fornecedor)), SMALL_B),
             Paragraph("", SMALL), Paragraph("", SMALL)],
            [Paragraph("Solicitante:", SMALL), Paragraph(escape(str(solicitante)), SMALL_B),
             Paragraph("Prazo de Entrega (em dias):", SMALL), Paragraph(escape(f"{prazo_entrega_dias} dias"), SMALL_B)],
        ],
        colWidths=grid_cols,
        rowHeights=[7 * mm, 7 * mm, 7 * mm, 7 * mm],
    )
    header_grid.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1.0, theme["BLACK"]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    # --- Área grande de descrição (uma linha de texto + campo grande) ---
    desc_tbl = Table(
        [[Paragraph(escape(desc_grande) if desc_grande else "&nbsp;", SMALL)]],
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

    def _build_tbl_servicos() -> Table:
        # colunas aproximadas do modelo
        col_w = [20 * mm, 75 * mm, 25 * mm, 22 * mm, content_w - (20 + 75 + 25 + 22) * mm]
        # na prática, a última coluna fica mais larga (onde entra a mini-tabela com R$ e valor)

        data: list[list[Any]] = []
        # faixa título
        data.append([Paragraph("Homem Hora / Maquina", BAR_WHITE), "", "", "", ""])
        # header colunas
        data.append(
            [
                Paragraph("Item", BAR_WHITE),
                Paragraph("Operação", BAR_WHITE),
                Paragraph("Qtd Horas", BAR_WHITE),
                Paragraph("Vlr Unit", BAR_WHITE),
                Paragraph("Vlr Total", BAR_WHITE),
            ]
        )

        max_rows = 10
        for idx in range(max_rows):
            if idx < len(itens_serv):
                it = itens_serv[idx]
                item_no = f"{idx+1:02d}"
                operacao = _get(it, "descricao", "descricao_item", "nome", default="-")
                qtd = _get(it, "quantidade", "qtd", default=0)
                unit = _get(it, "valor_unitario", "preco_unitario", "valorUnitario", default=0)
                total = getattr(it, "total", None)
                if total is None:
                    total = to_float(qtd) * to_float(unit)

                data.append(
                    [
                        Paragraph(escape(item_no), BASE_C),
                        Paragraph(escape(str(operacao)), SMALL),
                        Paragraph(escape(fmt_number(qtd)), BASE_C),
                        _money_cell(unit, bold=False),
                        _money_cell(total, bold=False),
                    ]
                )
            else:
                data.append(["", "", "", "", ""])

        t = Table(data, colWidths=col_w, rowHeights=[7 * mm, 7 * mm] + [7 * mm] * max_rows)
        t.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 1), theme["BLUE"]),
                    ("TEXTCOLOR", (0, 0), (-1, 1), theme["WHITE"]),
                    ("ALIGN", (0, 0), (-1, 1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    ("GRID", (0, 1), (-1, -1), 1.0, theme["BLACK"]),
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return t

    def _build_tbl_materiais() -> Table:
        col_w = [20 * mm, 75 * mm, 25 * mm, 22 * mm, content_w - (20 + 75 + 25 + 22) * mm]

        data: list[list[Any]] = []
        data.append([Paragraph("Material ( Matéria-Prima)", BAR_WHITE), "", "", "", ""])
        data.append(
            [
                Paragraph("Item", BAR_WHITE),
                Paragraph("Descrição", BAR_WHITE),
                Paragraph("Qtd kg", BAR_WHITE),
                Paragraph("Vlr Unit", BAR_WHITE),
                Paragraph("Vlr Total", BAR_WHITE),
            ]
        )

        max_rows = 8
        for idx in range(max_rows):
            if idx < len(itens_mat):
                it = itens_mat[idx]
                item_no = f"{idx+1:02d}"
                desc = _get(it, "descricao", "descricao_item", "nome", default="-")
                qtd = _get(it, "quantidade", "qtd", default=0)
                unit = _get(it, "valor_unitario", "preco_unitario", "valorUnitario", default=0)
                total = getattr(it, "total", None)
                if total is None:
                    total = to_float(qtd) * to_float(unit)

                data.append(
                    [
                        Paragraph(escape(item_no), BASE_C),
                        Paragraph(escape(str(desc)), SMALL),
                        Paragraph(escape(fmt_number(qtd)), BASE_C),
                        _money_cell(unit, bold=False),
                        _money_cell(total, bold=False),
                    ]
                )
            else:
                data.append(["", "", "", "", ""])

        t = Table(data, colWidths=col_w, rowHeights=[7 * mm, 7 * mm] + [7 * mm] * max_rows)
        t.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (-1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 1), theme["BLUE"]),
                    ("TEXTCOLOR", (0, 0), (-1, 1), theme["WHITE"]),
                    ("ALIGN", (0, 0), (-1, 1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    ("GRID", (0, 1), (-1, -1), 1.0, theme["BLACK"]),
                    ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),

                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )
        return t

    total_geral = sum_totais_itens(itens_list)

    total_tbl = Table(
        [[Paragraph("Valor Total do Orçamento", BAR_WHITE), Paragraph("R$", SMALL_B), Paragraph(escape(fmt_money_no_prefix(total_geral)), BOLD_R)]],
        colWidths=[content_w - 45 * mm, 10 * mm, 35 * mm],
        rowHeights=[8 * mm],
    )
    total_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), theme["BLUE"]),
                ("TEXTCOLOR", (0, 0), (0, 0), theme["WHITE"]),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
                ("GRID", (0, 0), (-1, -1), 1.0, theme["BLACK"]),

                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    aprov_bar = Table(
        [[Paragraph("Aprovação do Orçamento", BAR_WHITE)]],
        colWidths=[content_w],
        rowHeights=[8 * mm],
    )
    aprov_bar.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), theme["BLUE"]),
                ("TEXTCOLOR", (0, 0), (-1, -1), theme["WHITE"]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 1.2, theme["BLACK"]),
            ]
        )
    )

    sign_tbl = Table(
        [
            ["", "", ""],
            [Paragraph("________________________________", BASE_C),
             Paragraph("________________________________", BASE_C),
             Paragraph("________________________________", BASE_C)],
            [Paragraph("Solicitante da Aço\nCearense", BASE_C),
             Paragraph("Responsável\nTécnico da Aço\nCearense", BASE_C),
             Paragraph("Responsável da\nCONTRATADA", BASE_C)],
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

    # =========================
    # MONTA ELEMENTOS (fluxo)
    # =========================
    elements: list[Any] = []
    elements.append(Paragraph("Anexo V - Formulário de Orçamento", TITLE_TOP))
    elements.append(Spacer(1, 4))

    # Box “principal” do formulário é composto por tabelas empilhadas.
    elements.append(top_header)
    elements.append(header_grid)
    elements.append(desc_tbl)
    elements.append(_build_tbl_servicos())
    elements.append(Spacer(1, 3))
    elements.append(_build_tbl_materiais())
    elements.append(total_tbl)
    elements.append(aprov_bar)
    elements.append(sign_tbl)

    doc.build(elements)
    return buf.getvalue()
