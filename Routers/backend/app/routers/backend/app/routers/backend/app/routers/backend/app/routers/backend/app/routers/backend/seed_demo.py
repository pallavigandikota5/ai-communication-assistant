from app.db import SessionLocal, init_db
from app.models import Email, DraftResponse
from app.utils.rag import retrieve_simple, generate_reply
from app.utils.nlp import detect_sentiment, detect_priority, summarize, extract_contacts
from datetime import datetime, timedelta
import json

init_db()
db = SessionLocal()

samples = [
    {
        "sender":"alice@example.com",
        "subject":"Support: Cannot access my account ASAP",
        "body":"Hi team, I cannot access my account since morning. It says 'invalid session'. Please fix immediately. My phone is +1 555-234-7788.",
        "received_at": datetime.utcnow() - timedelta(hours=2)
    },
    {
        "sender":"bob@example.com",
        "subject":"Request: Refund for order #1234",
        "body":"Hello, I'd like to request a refund for order #1234. The product didn't work as expected. Kindly assist.",
        "received_at": datetime.utcnow() - timedelta(hours=5)
    },
    {
        "sender":"chris@example.com",
        "subject":"Query: Supported browsers?",
        "body":"Quick question: which browsers are officially supported for your product?",
        "received_at": datetime.utcnow() - timedelta(hours=12)
    }
]

for it in samples:
    sentiment = detect_sentiment(it["body"])
    priority = detect_priority(it["subject"], it["body"])
    contacts = extract_contacts(it["body"])
    email_row = Email(
        sender=it["sender"],
        subject=it["subject"],
        body=it["body"],
        received_at=it["received_at"],
        sentiment=sentiment,
        priority=priority,
        summary=summarize(it["body"]),
        status="pending",
        phone=(contacts["phones"][0] if contacts["phones"] else None),
        alt_email=None,
        meta=json.dumps({"contacts":contacts})
    )
    db.add(email_row); db.commit(); db.refresh(email_row)
    ctx = retrieve_simple(it["body"], k=4)
    draft = generate_reply(it["body"], ctx)
    db.add(DraftResponse(email_id=email_row.id, draft=draft)); db.commit()

db.close()
print("Seeded demo data.")
