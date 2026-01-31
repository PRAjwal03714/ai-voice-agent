"""
Database models and connection for PostgreSQL
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env file (won't override existing env vars from Docker)
# load_dotenv()  # Disabled for Docker

# Get database URL from environment (Docker Compose will set this)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:132506@localhost:5432/vanessa_ai")


# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    intent = Column(String)
    price_mentioned = Column(Float, nullable=True)
    timeline_mentioned = Column(String, nullable=True)
    call_duration = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def save_call_data(call_sid, phone_number, intent, price_mentioned=None, timeline_mentioned=None, call_duration=None):
    """Save call data to database"""
    db = SessionLocal()
    try:
        call_log = CallLog(
            call_sid=call_sid,
            phone_number=phone_number,
            intent=intent,
            price_mentioned=price_mentioned,
            timeline_mentioned=timeline_mentioned,
            call_duration=call_duration
        )
        db.add(call_log)
        db.commit()
        print(f"✅ Saved call to database: {call_sid}")
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()
