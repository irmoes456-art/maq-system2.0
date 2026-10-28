"""Laudo Mastermaq digital (PDF) — mesmo layout da pré-visualização, em azul/vermelho, fundo branco e texto preto."""
import asyncio
import io
import os
import uuid
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from laudo_generator import _decode_base64_image, _to_jpeg_bytes

BLUE = colors.HexColor("#1a3a8f")
RED = colors.HexColor("#c8102e")
LOGO = Path(__file__).parent / "assets" / "mastermaq-logo.png"
PHOTO_LABELS = [
    "FOTO 1 – Instalação do Produto", "FOTO 2 – Instalação do Produto",
    "FOTO 3 – Local onde o Produto está Instalado", "FOTO 4 – Instalação Elétrica",
    "FOTO 5 – Nº de Serie", "FOTO 6 – Peça Avariada",
    "FOTO 7 – Defeito/Erro Encontrado", "FOTO 8 – Defeito/Erro Encontrado",
]
COMPANY = ("<b>MASTERMAQ ASSISTÊNCIA TÉCNICA</b><br/>Conserto de Geladeiras e Eletrodomésticos Belo Horizonte – MG<br/>"
           "CNPJ: 19955560/0001-28<br/>Telefone: 31 3422-5293 / 31 2526-8420")

_s = lambda size=8.5, bold=False, color=colors.black, align=0: ParagraphStyle(  # noqa: E731
    "x", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size, leading=size * 1.3, textColor=color, alignment=align)


def _p(text, **kw):
    return Paragraph(escape(str(text or "")).replace("\n", "<br/>"), _s(**kw))


def _grid(rows, widths, label_cols=(0,), spans=()):
    t = Table(rows, colWidths=widths)
    st = [("GRID", (0, 0), (-1, -1), 0.6, BLUE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BACKGROUND", (0, 0), (-1, -1), colors.white), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    st += list(spans)
    t.setStyle(TableStyle(st))
    return t


def _photo(raw):
    data = _decode_base64_image(raw) if raw else None
    if not data:
        return Spacer(1, 40 * mm)
    img = Image(io.BytesIO(_to_jpeg_bytes(data)))
    ratio = min(84 * mm / img.imageWidth, 52 * mm / img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth * ratio, img.imageHeight * ratio
    return img


def build_pdf(d: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=12 * mm, rightMargin=12 * mm, topMargin=10 * mm, bottomMargin=10 * mm,
                            title=f"Laudo Mastermaq OS {d.get('os_number', '')}")
    W = doc.width
    logo = Image(str(LOGO), width=42 * mm, height=42 * mm * 329 / 669)
    head = Table([[logo, Paragraph(COMPANY, _s(9))]], colWidths=[48 * mm, W - 48 * mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, 0), 2.5, BLUE)]))
    bar = Table([[_p("RELATÓRIO DE ATENDIMENTO AO CLIENTE", size=11, bold=True, color=BLUE),
                  _p(f"OS {d.get('os_number', '')}", size=11, bold=True, color=RED, align=2)]], colWidths=[W * 0.7, W * 0.3])
    bar.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 1.5, RED)]))
    L = lambda t: _p(t, bold=True)  # noqa: E731
    brand = (d.get("brand") or "").strip()
    info = _grid([
        [L("NÚMERO OS"), _p(d.get("os_number")), L("ASSISTÊNCIA TÉC."), _p("MASTERMAQ")],
        [L("NOME DO CLIENTE"), _p(d.get("customer_name")), "", ""],
        [L("MODELO DO PROD."), _p(d.get("model")), L("Nº DE SÉRIE"), _p(d.get("serial_number"))],
        [L("ART ou Batch"), _p(d.get("batch")), L("MARCA"), _p(brand)],
    ], [34 * mm, W / 2 - 34 * mm, 34 * mm, W / 2 - 34 * mm], spans=[("SPAN", (1, 1), (3, 1))])
    defect = _grid([
        [L("DEFEITO RELATADO PELO CLIENTE"), _p(d.get("reported_defect"))],
        [L("DIAGNÓSTICO TÉCNICO"), _p(d.get("technical_diagnosis"))],
        [L("INSTALAÇÃO CORRETA?"), _p(d.get("installation_correct"))],
        [L("PEÇAS NECESSÁRIAS PARA REPARO"), _p(d.get("required_parts"))],
    ], [50 * mm, W - 50 * mm])
    imgs = list(d.get("images") or []) + [""] * 8
    cells = [[_p(PHOTO_LABELS[i], size=7.5, bold=True, color=RED), _photo(imgs[i])] for i in range(8)]
    rows = []
    for i in range(0, 8, 2):
        rows += [[cells[i][0], cells[i + 1][0]], [cells[i][1], cells[i + 1][1]]]
    photos = Table(rows, colWidths=[W / 2, W / 2])
    photos.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, BLUE), ("INNERGRID", (0, 0), (-1, -1), 0.4, BLUE),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    v = [d.get("voltage_f1f2"), d.get("voltage_f1_terra"), d.get("voltage_f2_terra")]
    volt = _grid([[L("Detalhamento da Tensão de Alimentação do Produto:")],
                  [_p(f"F1+F2: {v[0] or '—'}V   |   F1+Terra: {v[1] or '—'}V   |   F2+Terra: {v[2] or '—'}V" if any(v) else "", align=1)]], [W])
    notes = _grid([[L("Anotações Técnicas:")], [_p(f"Observações técnicas: {d.get('technical_notes') or ''}")],
                   [_p(d.get("final_status"))]], [W])
    when = d.get("date") or datetime.now().strftime("%d/%m/%Y")
    foot = Table([[_p(f"{d.get('location') or 'BELO HORIZONTE'}, {when}", align=1)], [Spacer(1, 12 * mm)],
                  [_p(d.get("technician"), bold=True, align=1)], [_p("Técnico Responsável", size=7.5, align=1)],
                  [_p(f"Data de emissão do Laudo: {datetime.now().strftime('%d/%m/%Y')}", size=7, align=1)]], colWidths=[W])
    foot.setStyle(TableStyle([("LINEABOVE", (0, 2), (0, 2), 0.8, BLUE)]))
    sp = Spacer(1, 3 * mm)
    doc.build([head, sp, bar, sp, info, defect, sp, photos, sp, volt, notes, sp, foot])
    return buf.getvalue()


async def create(d: dict) -> dict:
    """Gera o PDF e guarda no storage permanente. Devolve link público."""
    from manuais_module import put_object
    token = uuid.uuid4().hex
    pdf = await asyncio.to_thread(build_pdf, d)
    await asyncio.to_thread(put_object, f"mastermaq-manuais/shared-pdfs/{token}.pdf", pdf, "application/pdf")
    path = f"/api/files/temp-pdf/{token}"
    return {"path": path, "url": f"{os.environ.get('PUBLIC_BACKEND_URL') or ''}{path}"}
