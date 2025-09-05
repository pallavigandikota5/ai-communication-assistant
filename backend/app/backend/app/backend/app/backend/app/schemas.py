from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class EmailOut(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_at: datetime
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    summary: Optional[str] = None
    status: str
    phone: Optional[str] = None
    alt_email: Optional[str] = None
    meta: Optional[Any] = None

    class Config:
        from_attributes = True

class DraftResponseOut(BaseModel):
    id: int
    email_id: int
    draft: str
    created_at: datetime
    sent: bool

    class Config:
        from_attributes = True

class SendRequest(BaseModel):
    email_id: int
    to: str
    subject: str
    body: str
