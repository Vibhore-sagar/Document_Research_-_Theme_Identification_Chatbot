# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Base

DATABASE_URL = "sqlite:///./backend/data/documents.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
