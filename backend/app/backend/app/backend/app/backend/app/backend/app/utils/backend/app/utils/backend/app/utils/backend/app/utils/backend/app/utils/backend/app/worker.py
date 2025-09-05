from .utils.imap_client import fetch_filtered
from .db import SessionLocal
from .models import Email, DraftResponse
from .utils.nlp import detect_sentiment, detect_priority, extract_contacts, summarize
from .utils.rag import retrieve_simple, generate_reply
import json

def fetch_and_process_emails():
    items = fetch_filtered(limit=100)
    if not items:
        return
    db = SessionLocal()
    try:
        for it in items:
            exists = db.query(Email).filter(Email.sender==it["sender"], Email.subject==it["subject"]).first()
            if exists:
                continue
            sentiment = detect_sentiment(it["body"])
            priority = detect_priority(it["subject"], it["body"])
            contacts = extract_contacts(it["body"])
            phone = contacts["phones"][0] if contacts["phones"] else None
            alt_email = None
            for e in contacts["emails"]:
                if e.lower() != (it["sender"] or "").lower():
                    alt_email = e; break
            email_row = Email(
                sender=it["sender"],
                subject=it["subject"],
                body=it["body"],
                received_at=it["received_at"],
                sentiment=sentiment,
                priority=priority,
                summary=summarize(it["body"]),
                status="pending",
                phone=phone,
                alt_email=alt_email,
                meta=json.dumps({"contacts":contacts})
            )
            db.add(email_row); db.commit(); db.refresh(email_row)
            ctx = retrieve_simple(it["body"], k=4)
            draft = generate_reply(it["body"], ctx)
            dr = DraftResponse(email_id=email_row.id, draft=draft)
            db.add(dr); db.commit()
    finally:
        db.close()
