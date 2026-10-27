"""Mi agent: memória persistente, ações (roteiros/OSs), PDFs, anexos e regiões de Sabará."""
import io
import re
import json
import uuid
import asyncio
import logging
import unicodedata
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _n(s) -> str:
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower().strip()


REGIONS = {
    "Regional Sede (Centro Histórico e Entorno)": ["Adelmolândia", "Alto do Cabral", "Alto São Francisco", "Arraial Velho",
        "Centro", "Coração de Jesus", "Esplanada", "Mangabeiras", "Morro São Francisco", "Paciência", "Siderúrgica", "Vila Santa Rita"],
    "Distrito de Carvalho de Brito (Eixo General Carneiro / divisa com BH)": ["Alvorada", "Castanheiras", "General Carneiro",
        "Itacolomi", "Nações Unidas", "Novo Alvorada", "Roça Grande", "Santo Antônio de Roça Grande", "Vila Michel"],
    "Regional Ana Lúcia / Nova Vista": ["Ana Lúcia", "Bom Retiro", "Nova Vista", "Novo Santa Inês", "Rio Negro", "Vila Ribeiro"],
    "Regional Borges / Km 14": ["Borges", "Km 14", "Morada da Serra", "Pompéu"],
    "Distrito de Ravena": ["Ravena", "Centro de Ravena"],
    "Distrito de Mestre Caetano": ["Mestre Caetano", "Km 25"],
}
REGION_KEYS = {  # termos que identificam a regional na pergunta
    "Regional Sede (Centro Histórico e Entorno)": ["regional sede", "centro historico"],
    "Distrito de Carvalho de Brito (Eixo General Carneiro / divisa com BH)": ["carvalho de brito", "general carneiro"],
    "Regional Ana Lúcia / Nova Vista": ["ana lucia", "nova vista"],
    "Regional Borges / Km 14": ["borges", "km 14"],
    "Distrito de Ravena": ["ravena"],
    "Distrito de Mestre Caetano": ["mestre caetano"],
}


def regions_text() -> str:
    return "\n".join(f"- {r}: {', '.join(b)}" for r, b in REGIONS.items())


def region_context(q: str, docs: list) -> str:
    """OSs de Sabará cuja bairro pertence à regional citada na pergunta."""
    nq = _n(q)
    if "sabara" not in nq and not any(k in nq for ks in REGION_KEYS.values() for k in ks):
        return ""
    out = []
    for region, keys in REGION_KEYS.items():
        if not any(k in nq for k in keys) and "sabara" not in nq:
            continue
        bairros = {_n(b) for b in REGIONS[region]}
        hits = [d for d in docs if "sabara" in _n(d.get("city")) and _n(d.get("neighborhood")) in bairros]
        if not any(k in nq for k in keys) and not hits:
            continue
        out.append(f"{region}: {len(hits)} OSs")
        out += [f"- OS {d.get('os_number')}; status {d.get('status')}; {d.get('address') or ''} {d.get('number') or ''}, "
                f"{d.get('neighborhood')}; cliente {d.get('customer_name') or ''}; {d.get('product') or d.get('model') or ''}"
                for d in hits[:80]]
    return "\n".join(out)


# --- Memória persistente (por usuário, vale para todas as conversas) ---
async def get_memories(mongo_db, email: str):
    return await mongo_db["mi_memories"].find({"user_email": email}, {"_id": 0}).sort("created_at", -1).to_list(200)


async def remember(mongo_db, email: str, fact: str):
    fact = (fact or "").strip()
    if fact:
        await mongo_db["mi_memories"].insert_one({"id": str(uuid.uuid4()), "user_email": email, "fact": fact[:1000],
                                                  "created_at": datetime.now(timezone.utc).isoformat()})


# --- Ações ---
ACTIONS_PROMPT = (
    "AÇÕES: você pode agir no sistema. Quando o usuário pedir (ou quando for claramente útil), inclua no FINAL da resposta "
    "um bloco <acoes>[...]</acoes> com um array JSON. Tipos:\n"
    '- {"type":"remember","fact":"..."} → guarda na memória permanente (use sempre que o usuário pedir para lembrar, '
    "ou contar preferência/fato duradouro).\n"
    '- {"type":"create_route","name":"...","technician":"...","date":"AAAA-MM-DD","os_numbers":["..."]} (máx. 9 OSs)\n'
    '- {"type":"update_route","route":"nome ou id","fields":{"date":"AAAA-MM-DD","technician":"...","status":"Pendente|Em andamento|Concluído|Cancelado","name":"..."},'
    '"add_os":["..."],"remove_os":["..."]}\n'
    '- {"type":"update_os","os_number":"...","fields":{"status":"...","technician":"...","observations":"...","attendance_date":"AAAA-MM-DD", ...}}\n'
    '- {"type":"create_os","fields":{"customer_name":"...","phone1":"...","cep":"...","address":"...","number":"...","complement":"...",'
    '"neighborhood":"...","city":"...","product":"...","brand":"...","model":"...","reported_defect":"...","service_type":"..."}} '
    "(número da OS é gerado automaticamente se não informado)\n"
    '- {"type":"edit_docx","replacements":[{"find":"texto exato do documento","replace":"novo texto"}],"pdf":false} → edita o '
    "DOCX anexado mantendo layout e todo o resto do conteúdo igual (só troca os trechos indicados; use pdf=true para entregar em PDF).\n"
    '- {"type":"generate_pdf","title":"...","content":"texto completo do documento"} → gera PDF novo do zero e devolve link.\n'
    "Ações create_route/update_route/update_os/create_os ficam aguardando o usuário clicar em Confirmar; diga isso em uma frase. "
    "Nunca escreva o JSON fora do bloco <acoes>."
)
OS_EDITABLE = {"status", "technician", "observations", "attendance_date", "priority", "reported_defect", "technical_diagnosis",
               "required_parts", "customer_name", "phone1", "address", "number", "neighborhood", "city", "model",
               "serial_number", "product", "service_type"}
CONFIRM_TYPES = {"create_route", "update_route", "update_os", "create_os"}
CREATE_OS = None  # injetado pelo server.py (cria OS reutilizando o endpoint)


def parse_actions(answer: str):
    m = re.search(r"<acoes>(.*?)</acoes>", answer or "", re.S)
    if not m:
        return answer, []
    try:
        acts = json.loads(m.group(1).strip())
        acts = acts if isinstance(acts, list) else [acts]
    except Exception:
        acts = []
    return (answer[:m.start()] + answer[m.end():]).strip(), [a for a in acts if isinstance(a, dict) and a.get("type")]


def summarize(a: dict) -> str:
    t = a.get("type")
    if t == "create_route":
        return f"Criar roteiro \"{a.get('name') or 'Roteiro'}\" — {a.get('technician')}, {a.get('date')}, OSs {', '.join(map(str, a.get('os_numbers') or []))}"
    if t == "update_route":
        extra = [f"{k}={v}" for k, v in (a.get("fields") or {}).items()]
        if a.get("add_os"):
            extra.append("+OS " + ", ".join(map(str, a["add_os"])))
        if a.get("remove_os"):
            extra.append("-OS " + ", ".join(map(str, a["remove_os"])))
        return f"Alterar roteiro \"{a.get('route')}\": {'; '.join(extra)}"
    if t == "update_os":
        return f"Alterar OS {a.get('os_number')}: " + "; ".join(f"{k}={v}" for k, v in (a.get("fields") or {}).items())
    if t == "create_os":
        return "Criar OS: " + "; ".join(f"{k}={v}" for k, v in (a.get("fields") or {}).items() if v)
    return t


async def _route_orders(db, os_numbers):
    orders = []
    for i, num in enumerate(os_numbers, 1):
        d = await db.service_orders.find_one({"os_number": str(num)}, {"_id": 0})
        if not d:
            raise ValueError(f"OS {num} não encontrada")
        orders.append({k: d.get(k) for k in ("os_number", "customer_name", "neighborhood", "city", "address", "number",
                                             "phone1", "lat", "lng", "attendance_date", "status")} | {"sequence": i})
    return orders


async def execute(db, a: dict, payload: dict = None):
    """Executa ação confirmada. Retorna texto de resultado."""
    from routes_module import create_route, update_route, RouteCreate, RouteUpdate
    t = a["type"]
    if t == "create_os":
        r = await CREATE_OS(dict(a.get("fields") or {}), payload or {})
        num = r.get("os_number") if isinstance(r, dict) else getattr(r, "os_number", None)
        return f"OS {num} criada."
    if t == "create_route":
        nums = list(a.get("os_numbers") or [])[:9]
        r = await create_route(RouteCreate(name=a.get("name"), technician=a.get("technician") or "", date=a.get("date") or "",
                                           orders=await _route_orders(db, nums)))
        return f"Roteiro \"{r.get('name')}\" criado com {len(nums)} OSs."
    if t == "update_route":
        ref = str(a.get("route") or "")
        route = await db.routes.find_one({"id": ref}, {"_id": 0}) or await db.routes.find_one({"name": ref}, {"_id": 0})
        if not route:
            raise ValueError(f"Roteiro \"{ref}\" não encontrado")
        fields = {k: v for k, v in (a.get("fields") or {}).items() if k in {"date", "technician", "status", "name"}}
        if a.get("add_os") or a.get("remove_os"):
            remove = {str(x) for x in a.get("remove_os") or []}
            keep = [str(o["os_number"]) for o in route.get("orders") or [] if str(o.get("os_number")) not in remove]
            fields["orders"] = await _route_orders(db, (keep + [str(x) for x in a.get("add_os") or [] if str(x) not in keep])[:9])
        await update_route(route["id"], RouteUpdate(**fields))
        return f"Roteiro \"{route.get('name')}\" atualizado."
    if t == "update_os":
        fields = {k: v for k, v in (a.get("fields") or {}).items() if k in OS_EDITABLE}
        if not fields:
            raise ValueError("Nenhum campo permitido para alterar")
        fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        if "observations" in fields:  # acrescenta, não apaga (ex: "[SITE] Taxa de visita PAGA")
            cur = await db.service_orders.find_one({"os_number": str(a.get("os_number"))}, {"observations": 1}) or {}
            if cur.get("observations"):
                fields["observations"] = f"{cur['observations']}\n{fields['observations']}"
        res = await db.service_orders.update_one({"os_number": str(a.get("os_number"))}, {"$set": fields})
        if not res.matched_count:
            raise ValueError(f"OS {a.get('os_number')} não encontrada")
        return f"OS {a.get('os_number')} atualizada."
    raise ValueError(f"Ação desconhecida: {t}")


# --- PDF ---
def _build_pdf(title: str, content: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from xml.sax.saxutils import escape
    buf = io.BytesIO()
    st = getSampleStyleSheet()
    story = [Paragraph(escape(title or "Documento"), st["Title"]), Spacer(1, 12)]
    for line in (content or "").split("\n"):
        txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(line.strip()))
        story.append(Paragraph(txt, st["Normal"]) if txt else Spacer(1, 8))
    SimpleDocTemplate(buf, pagesize=A4, title=title or "Documento").build(story)
    return buf.getvalue()


async def generate_pdf(title: str, content: str) -> str:
    from manuais_module import put_object
    token = uuid.uuid4().hex
    data = await asyncio.to_thread(_build_pdf, title, content)
    await asyncio.to_thread(put_object, f"mastermaq-manuais/shared-pdfs/{token}.pdf", data, "application/pdf")
    return f"/api/files/temp-pdf/{token}"


# --- Anexos ---
FILE_PREFIX = "mastermaq-manuais/mi-files"


def _replace_in_paragraph(p, find: str, repl: str) -> bool:
    """Troca texto preservando a formatação do primeiro run do trecho."""
    if find not in p.text:
        return False
    if any(find in r.text for r in p.runs):
        for r in p.runs:
            if find in r.text:
                r.text = r.text.replace(find, repl)
        return True
    full = p.text.replace(find, repl)
    for i, r in enumerate(p.runs):
        r.text = full if i == 0 else ""
    return True


def _edit_docx(data: bytes, replacements: list) -> tuple:
    import docx
    doc = docx.Document(io.BytesIO(data))
    paras = list(doc.paragraphs)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                paras += cell.paragraphs
    for sec in doc.sections:
        paras += sec.header.paragraphs + sec.footer.paragraphs
    done = 0
    for rp in replacements:
        f, r = str(rp.get("find") or ""), str(rp.get("replace") or "")
        if f:
            done += sum(_replace_in_paragraph(p, f, r) for p in paras)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue(), done


def _docx_to_pdf(data: bytes) -> bytes:
    import os
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "doc.docx")
        open(src, "wb").write(data)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", d, src], capture_output=True, timeout=180)
        return open(os.path.join(d, "doc.pdf"), "rb").read()


async def edit_docx(file_id: str, replacements: list, as_pdf: bool) -> tuple:
    from manuais_module import get_object, put_object
    src, _ = await asyncio.to_thread(get_object, f"{FILE_PREFIX}/{file_id}.docx")
    out, done = await asyncio.to_thread(_edit_docx, src, replacements)
    ext, ctype = "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if as_pdf:
        out, ext, ctype = await asyncio.to_thread(_docx_to_pdf, out), "pdf", "application/pdf"
    token = uuid.uuid4().hex
    await asyncio.to_thread(put_object, f"{FILE_PREFIX}/{token}.{ext}", out, ctype)
    return f"/api/mi/files/{token}.{ext}", done


async def store_upload(data: bytes) -> str:
    from manuais_module import put_object
    fid = uuid.uuid4().hex
    await asyncio.to_thread(put_object, f"{FILE_PREFIX}/{fid}.docx", data,
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    return fid


def extract_upload(data: bytes, filename: str) -> str:
    import subprocess
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "pdf":
        return subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True, timeout=120).stdout.decode(errors="ignore")
    if ext == "docx":
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    if ext in ("txt", "md", "csv", "json"):
        return data.decode(errors="ignore")
    raise ValueError("Formato não suportado (use PDF, DOCX, TXT ou CSV)")
