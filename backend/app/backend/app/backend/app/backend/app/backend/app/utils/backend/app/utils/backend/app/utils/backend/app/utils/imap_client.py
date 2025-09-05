import os
from datetime import datetime, timezone, timedelta
from imapclient import IMAPClient
import email
from email.header import decode_header

HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
PORT = int(os.getenv("IMAP_PORT", "993"))
EMAIL = os.getenv("IMAP_EMAIL")
PASSWORD = os.getenv("IMAP_PASSWORD")
FOLDER = os.getenv("IMAP_FOLDER", "INBOX")
USE_SSL = os.getenv("IMAP_USE_SSL", "true").lower() == "true"

FILTER_TERMS = ["support", "query", "request", "help"]

def _decode(s):
    if not s:
        return ""
    parts = decode_header(s)
    out = ""
    for txt, enc in parts:
        if isinstance(txt, bytes):
            out += txt.decode(enc or "utf-8", errors="ignore")
        else:
            out += txt
    return out

def _extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    continue
        return ""
    payload = msg.get_payload(decode=True)
    try:
        return payload.decode(errors="ignore")
    except Exception:
        return str(payload)

def fetch_filtered(limit: int = 50):
    if not EMAIL or not PASSWORD:
        return []
    with IMAPClient(HOST, port=PORT, ssl=USE_SSL) as server:
        server.login(EMAIL, PASSWORD)
        server.select_folder(FOLDER)
        since = (datetime.now(timezone.utc) - timedelta(days=7))
        messages = server.search(['SINCE', since.strftime("%d-%b-%Y")])
        resp = server.fetch(messages[-limit:], ['ENVELOPE', 'RFC822'])
        result = []
        for _, data in resp.items():
            raw = data[b'RFC822']
            msg = email.message_from_bytes(raw)
            subject = _decode(msg.get('Subject') or "")
            if not any(t.lower() in subject.lower() for t in FILTER_TERMS):
                continue
            from_addr = email.utils.parseaddr(msg.get('From'))[1]
            date_str = msg.get('Date')
            body = _extract_body(msg)
            dt = datetime.now(timezone.utc)
            try:
                dt = email.utils.parsedate_to_datetime(date_str)
            except Exception:
                pass
            result.append({
                "sender": from_addr,
                "subject": subject,
                "body": body,
                "received_at": dt
            })
        return result
