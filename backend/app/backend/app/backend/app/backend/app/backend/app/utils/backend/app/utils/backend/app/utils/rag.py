import os, glob
from typing import List, Tuple
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

def load_kb_texts(kb_dir: str = "kb") -> List[Tuple[str, str]]:
    chunks = []
    for path in glob.glob(os.path.join(kb_dir, "**", "*.*"), recursive=True):
        if os.path.isdir(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            txt = ""
        if txt.strip():
            chunks.append((path, txt))
    return chunks

def retrieve_simple(query: str, k: int = 4) -> List[str]:
    docs = load_kb_texts()
    q = query.lower().split()
    scored = []
    for _, txt in docs:
        score = sum(txt.lower().count(w) for w in q)
        scored.append((score, txt))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for s, t in scored[:k] if s > 0]

def generate_reply(prompt: str, context_docs: List[str]) -> str:
    ctx = "\n\n---\n\n".join(context_docs[:4]) if context_docs else "No KB context."
    system = "You are a professional, empathetic support assistant. Keep responses concise and actionable."
    user = f"Context:\n{ctx}\n\nUser Email:\n{prompt}\n\nWrite a helpful, empathetic reply."
    if not OPENAI_API_KEY:
        return ("[DRAFT REPLY]\nThanks for reaching out. We understand your concern and are here to help.\n"
                "1) Check status page. 2) Try password reset.\nIf it persists, share logs.\n— Support Team")
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()
