from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Email, DraftResponse
from ..schemas import EmailOut, DraftResponseOut
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[EmailOut])
def list_emails(db: Session = Depends(get_db)):
    q = db.query(Email).order_by(Email.priority.desc(), Email.received_at.desc())
    return q.all()

@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    e = db.get(Email, email_id)
    if not e:
        raise HTTPException(404, "Not found")
    return e

@router.get("/{email_id}/draft", response_model=DraftResponseOut)
def get_draft(email_id: int, db: Session = Depends(get_db)):
    dr = db.query(DraftResponse).filter(DraftResponse.email_id==email_id).order_by(DraftResponse.created_at.desc()).first()
    if not dr:
        raise HTTPException(404, "No draft")
    return dr
