# backend/app/models/document.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
