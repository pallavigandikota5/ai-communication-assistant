import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, List

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

URGENT_PATTERNS = [
    r"\burgent\b", r"\bimmediately\b", r"\bcritical\b", r"\bpriority\b",
    r"\bcannot access\b", r"\bdown\b", r"\bfailing\b", r"\bASAP\b", r"\bblocked\b"
]

CONTACT_EMAIL_RE = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
CONTACT_PHONE_RE = r"(\+?\d[\d\-\s]{7,}\d)"

def detect_sentiment(text: str) -> str:
    s = sia.polarity_scores(text or "")
    comp = s["compound"]
    if comp >= 0.25:
        return "positive"
    if comp <= -0.25:
        return "negative"
    return "neutral"

def detect_priority(subject: str, body: str) -> str:
    blob = f"{subject}\n{body}".lower()
    for pat in URGENT_PATTERNS:
        if re.search(pat, blob):
            return "urgent"
    return "not_urgent"

def extract_contacts(text: str) -> Dict[str, List[str]]:
    emails = re.findall(CONTACT_EMAIL_RE, text or "")
    phones = [p.strip() for p in re.findall(CONTACT_PHONE_RE, text or "")]
    return {"emails": list(set(emails)), "phones": list(set(phones))}

def summarize(text: str, max_len: int = 240) -> str:
    t = (text or "").strip().replace("\n", " ")
    return (t[: max_len - 3] + "...") if len(t) > max_len else t
