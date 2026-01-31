"""
Lead list - maps phone numbers to properties
In real life, this would come from skip tracing, public records, etc.
"""

from database import SessionLocal, Base
from sqlalchemy import Column, String, Integer
from database import engine

class Lead(Base):
    """
    Maps phone numbers to properties
    """
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, index=True)
    address = Column(String)
    owner_name = Column(String, nullable=True)
    
    
# Create table
Base.metadata.create_all(bind=engine)


def get_property_for_phone(phone_number: str):
    """
    Look up which property belongs to this phone number
    """
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        if lead:
            return lead.address
        return None
    finally:
        db.close()


def add_lead(phone_number: str, address: str, owner_name: str = None):
    """
    Add a lead to the database
    """
    db = SessionLocal()
    try:
        lead = Lead(
            phone_number=phone_number,
            address=address,
            owner_name=owner_name
        )
        db.add(lead)
        db.commit()
        print(f"✅ Added lead: {phone_number} → {address}")
    except Exception as e:
        print(f"❌ Error adding lead: {e}")
        db.rollback()
    finally:
        db.close()
