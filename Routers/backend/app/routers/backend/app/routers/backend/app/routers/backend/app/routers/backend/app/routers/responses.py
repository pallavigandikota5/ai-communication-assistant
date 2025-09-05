from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Email, DraftResponse
from ..schemas import SendRequest
from ..utils.mailer import send_email

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send")
def send_response(payload: SendRequest, db: Session = Depends(get_db)):
    email = db.get(Email, payload.email_id)
    if not email:
        raise HTTPException(404, "Email not found")
    send_email(payload.to, payload.subject, payload.body)
    email.status = "replied"
    db.add(email); db.commit()
    dr = DraftResponse(email_id=email.id, draft=payload.body, sent=True)
    db.add(dr); db.commit()
    return {"ok": True}

@router.post("/{email_id}/resolve")
def resolve(email_id: int, db: Session = Depends(get_db)):
    e = db.get(Email, email_id)
    if not e:
        raise HTTPException(404, "Not found")
    e.status = "resolved"
    db.add(e); db.commit()
    return {"ok": True}
