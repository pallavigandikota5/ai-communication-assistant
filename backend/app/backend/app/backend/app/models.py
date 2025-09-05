from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255), index=True)
    subject = Column(String(500), index=True)
    body = Column(Text)
    received_at = Column(DateTime, index=True)
    sentiment = Column(String(20), index=True)
    priority = Column(String(20), index=True)   # 'urgent' | 'not_urgent'
    summary = Column(Text)
    status = Column(String(20), default="pending")  # pending | replied | resolved
    phone = Column(String(50), nullable=True)
    alt_email = Column(String(255), nullable=True)
    meta = Column(Text, nullable=True)  # JSON string

class DraftResponse(Base):
    __tablename__ = "draft_responses"
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, index=True)
    draft = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    sent = Column(Boolean, default=False)
