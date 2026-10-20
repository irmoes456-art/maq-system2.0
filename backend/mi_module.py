"""Mi — assistente IA com contexto de todas as OSs (Supabase) e do texto dos manuais (indexado no Mongo)."""
import os
import re
import time
import uuid
import asyncio
import logging
import subprocess
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from manuais_module import get_object, _convert_pptx_to_pdf

logger = logging.getLogger(__name__)
MODEL = "gpt-5.4"

OS_FIELDS = [
    "os_number", "customer_name", "status", "source", "brand", "model", "product", "service_type",
    "reported_defect", "technical_diagnosis", "required_parts", "city", "neighborhood", "serial_number",
    "registration_date", "attendance_date", "technician", "phone1", "observations", "updated_at",
]
STOP = set("""a o as os um uma de da do das dos em no na nos nas e ou que qual quais quanto quantos quantas
como para por com sem se ser sao tem ter foi esta estao isso esse essa este me meu minha voce mi
qual sobre mais menos muito todas todos tudo pelo pela ate ja nao sim ola oi""".split())

_os_cache = {"ts": 0.0, "docs": [], "blobs": [], "stats": ""}
_os_lock = asyncio.Lock()
_index_state = {"running": False, "last_check": 0.0}


def _norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return s.lower()


def _tokens(q: str):
    return [t for t in re.findall(r"[a-z0-9][a-z0-9./-]*", _norm(q)) if len(t) >= 3 and t not in STOP]


async def _load_os(db):
    async with _os_lock:
        if time.time() - _os_cache["ts"] < 600 and _os_cache["docs"]:
            return
        proj = {f: 1 for f in OS_FIELDS}
        docs, skip = [], 0
        while True:
            batch = await db.service_orders.find({}, proj).skip(skip).limit(1000).to_list(1000)
            docs += batch
            if len(batch) < 1000:
                break
            skip += 1000
        by_src_status = Counter((d.get("source") or "-", d.get("status") or "-") for d in docs)
        by_brand = Counter((d.get("brand") or "-").upper() for d in docs)
        lines = [f"Total de OSs no sistema: {len(docs)}", "Contagem por origem/status:"]
        lines += [f"- {s} | {st}: {n}" for (s, st), n in sorted(by_src_status.items())]
        lines.append("Top marcas: " + ", ".join(f"{b}: {n}" for b, n in by_brand.most_common(20)))
        _os_cache.update(ts=time.time(), docs=docs, stats="\n".join(lines),
                         blobs=[_norm(" ".join(str(v) for v in d.values() if v)) for d in docs])


def _search_os(q: str, limit: int = 25):
    toks = _tokens(q)
    nums = set(re.findall(r"\d{4,}", q))
    scored = []
    for d, blob in zip(_os_cache["docs"], _os_cache["blobs"]):
        s = (100 if str(d.get("os_number")) in nums else 0) + sum(1 for t in toks if t in blob)
        if s > 0:
            scored.append((s, d.get("updated_at") or "", d))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [d for _, _, d in scored[:limit]]


def _pdf_pages(pdf: bytes):
    out = subprocess.run(["pdftotext", "-layout", "-", "-"], input=pdf, capture_output=True, timeout=180)
    return out.stdout.decode(errors="ignore").split("\f")


def _extract_pages(data: bytes, ext: str, cached_pdf: Optional[bytes]):
    if ext == "pdf":
        return _pdf_pages(data)
    if ext in ("pptx", "ppt"):
        return _pdf_pages(cached_pdf or _convert_pptx_to_pdf(data))
    if ext == "docx":
        import io
        import docx
        return ["\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)]
    return []


async def index_manuals(db, mongo_db):
    """Indexa (1x por manual) o texto de cada página em mi_manual_chunks."""
    if _index_state["running"]:
        return
    _index_state.update(running=True, last_check=time.time())
    try:
        chunks_col, idx_col = mongo_db["mi_manual_chunks"], mongo_db["mi_manual_index"]
        await chunks_col.create_index([("text", "text"), ("title", "text")], default_language="portuguese")
        done = {d["manual_id"] async for d in idx_col.find({}, {"manual_id": 1})}
        manuals = await db.manuais.find({"is_deleted": False}, {"_id": 0}).to_list(1000)
        for m in manuals:
            if m["id"] in done:
                continue
            extra = " ".join(x for x in (m.get("brand"), m.get("category")) if x)
            title = f"{m.get('original_filename', '')}" + (f" ({extra})" if extra else "")
            try:
                data, _ = await asyncio.to_thread(get_object, m["storage_path"])
                meta = await mongo_db["manuais_preview"].find_one({"manual_id": m["id"]}) or {}
                cached = None
                if meta.get("pdf_cache_path"):
                    cached, _ = await asyncio.to_thread(get_object, meta["pdf_cache_path"])
                pages = await asyncio.to_thread(_extract_pages, data, (m.get("extension") or "").lower(), cached)
                docs = []
                for pnum, txt in enumerate(pages, 1):
                    txt = re.sub(r"[ \t]+", " ", txt).strip()
                    for i in range(0, len(txt), 1500):
                        docs.append({"manual_id": m["id"], "title": title, "page": pnum, "text": txt[i:i + 1600]})
                if docs:
                    await chunks_col.insert_many(docs)
                await idx_col.insert_one({"manual_id": m["id"], "title": title, "chunks": len(docs),
                                          "indexed_at": datetime.now(timezone.utc)})
                logger.info(f"[Mi] manual indexado: {title} ({len(docs)} trechos)")
            except Exception as e:
                logger.error(f"[Mi] falha ao indexar {title}: {e!r}")
    finally:
        _index_state["running"] = False


async def _search_manuals(mongo_db, q: str, limit: int = 8):
    toks = _tokens(q)
    if not toks:
        return []
    cur = mongo_db["mi_manual_chunks"].find(
        {"$text": {"$search": " ".join(toks)}},
        {"_id": 0, "title": 1, "page": 1, "text": 1, "score": {"$meta": "textScore"}},
    ).sort([("score", {"$meta": "textScore"})]).limit(limit)
    return await cur.to_list(limit)


SYSTEM = (
    "Você é a Mi, assistente da Mastermaq (assistência técnica de eletrodomésticos em Belo Horizonte). "
    "Responda sempre em português do Brasil, de forma direta e objetiva, usando markdown simples. "
    "Use SOMENTE os dados de contexto fornecidos (OSs do banco e trechos de manuais). "
    "Ao responder com base em manual, cite o nome do manual e a página. "
    "Se a informação não estiver no contexto, diga claramente que não encontrou — nunca invente números, "
    "códigos de erro, peças ou procedimentos."
)


class ChatBody(BaseModel):
    message: str
    conversation_id: Optional[str] = None


def setup_mi_routes(api_router: APIRouter, db, mongo_db, require_admin):
    convs, msgs = mongo_db["mi_conversations"], mongo_db["mi_messages"]

    async def _own_conv(cid: str, email: str):
        c = await convs.find_one({"id": cid, "user_email": email}, {"_id": 0})
        if not c:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")
        return c

    @api_router.get("/mi/conversations")
    async def list_convs(payload: dict = Depends(require_admin)):
        return await convs.find({"user_email": payload["email"]}, {"_id": 0}).sort("updated_at", -1).to_list(200)

    @api_router.get("/mi/conversations/{cid}/messages")
    async def list_msgs(cid: str, payload: dict = Depends(require_admin)):
        await _own_conv(cid, payload["email"])
        return await msgs.find({"conversation_id": cid}, {"_id": 0}).sort("created_at", 1).to_list(1000)

    @api_router.delete("/mi/conversations/{cid}")
    async def delete_conv(cid: str, payload: dict = Depends(require_admin)):
        await _own_conv(cid, payload["email"])
        await convs.delete_one({"id": cid})
        await msgs.delete_many({"conversation_id": cid})
        return {"ok": True}

    @api_router.get("/mi/status")
    async def mi_status(_: dict = Depends(require_admin)):
        return {
            "manuais_indexados": await mongo_db["mi_manual_index"].count_documents({}),
            "trechos": await mongo_db["mi_manual_chunks"].count_documents({}),
            "indexando": _index_state["running"],
        }

    @api_router.post("/mi/chat")
    async def mi_chat(body: ChatBody, payload: dict = Depends(require_admin)):
        text = (body.message or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Mensagem vazia")
        email = payload["email"]
        now = datetime.now(timezone.utc).isoformat()
        if body.conversation_id:
            conv = await _own_conv(body.conversation_id, email)
        else:
            conv = {"id": str(uuid.uuid4()), "user_email": email, "title": text[:60], "created_at": now, "updated_at": now}
            await convs.insert_one(dict(conv))
        cid = conv["id"]

        # Novos manuais enviados entram no índice em background (checa a cada 10 min).
        if time.time() - _index_state["last_check"] > 600:
            asyncio.create_task(index_manuals(db, mongo_db))

        history = await msgs.find({"conversation_id": cid}, {"_id": 0}).sort("created_at", -1).to_list(10)
        await msgs.insert_one({"id": str(uuid.uuid4()), "conversation_id": cid, "role": "user", "content": text, "created_at": now})

        await _load_os(db)
        hist_q = " ".join(m["content"] for m in history if m["role"] == "user")[-400:]
        os_hits = _search_os(f"{text} {hist_q}")
        man_hits = await _search_manuals(mongo_db, text)
        titles = [d["title"] async for d in mongo_db["mi_manual_index"].find({}, {"title": 1})]

        os_txt = "\n".join("; ".join(f"{k}={v}" for k, v in d.items() if v) for d in os_hits) or "(nenhuma OS relacionada)"
        man_txt = "\n\n".join(f"[{h['title']} — pág. {h['page']}]\n{h['text']}" for h in man_hits) or "(nenhum trecho encontrado)"
        hist_txt = "\n".join(f"{'Usuário' if m['role'] == 'user' else 'Mi'}: {m['content'][:1500]}" for m in reversed(history))
        prompt = (
            f"Data de hoje: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"## Resumo do banco de OSs\n{_os_cache['stats']}\n\n"
            f"## OSs relacionadas à pergunta\n{os_txt}\n\n"
            f"## Manuais disponíveis\n" + "\n".join(f"- {t}" for t in titles) + "\n\n"
            f"## Trechos de manuais relevantes\n{man_txt}\n\n"
            f"## Conversa anterior\n{hist_txt or '(início)'}\n\n"
            f"## Pergunta\n{text}"
        )
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            chat = LlmChat(api_key=os.environ["EMERGENT_LLM_KEY"], session_id=f"mi-{cid}", system_message=SYSTEM).with_model("openai", MODEL)
            answer = (await chat.send_message(UserMessage(text=prompt)) or "").strip()
        except Exception as e:
            logger.error(f"[Mi] LLM falhou: {e!r}")
            msg = "Saldo da Universal Key esgotado." if "Budget" in str(e) else "Falha ao consultar a IA."
            raise HTTPException(status_code=424, detail=msg)

        done = datetime.now(timezone.utc).isoformat()
        reply = {"id": str(uuid.uuid4()), "conversation_id": cid, "role": "assistant", "content": answer, "created_at": done}
        await msgs.insert_one(dict(reply))
        await convs.update_one({"id": cid}, {"$set": {"updated_at": done}})
        return {"conversation_id": cid, "title": conv["title"], "message": reply}
