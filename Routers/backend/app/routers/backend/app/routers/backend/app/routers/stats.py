from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..db import SessionLocal
from ..models import Email

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/overview")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Email).count()
    last24 = db.query(Email).filter(Email.received_at >= datetime.utcnow() - timedelta(hours=24)).count()
    resolved = db.query(Email).filter(Email.status=="resolved").count()
    pending = db.query(Email).filter(Email.status!="resolved").count()
    pos = db.query(Email).filter(Email.sentiment=="positive").count()
    neu = db.query(Email).filter(Email.sentiment=="neutral").count()
    neg = db.query(Email).filter(Email.sentiment=="negative").count()
    urg = db.query(Email).filter(Email.priority=="urgent").count()
    notu = db.query(Email).filter(Email.priority=="not_urgent").count()
    return {
        "total": total,
        "last24": last24,
        "resolved": resolved,
        "pending": pending,
        "sentiment": {"positive": pos, "neutral": neu, "negative": neg},
        "priority": {"urgent": urg, "not_urgent": notu}
    }
