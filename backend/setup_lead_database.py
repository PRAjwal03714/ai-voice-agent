"""
Create leads with addresses NOT in the RAG system
So RAG actually has to ESTIMATE using comparables
"""

import random
from lead_database import add_lead, Lead

# Real Indianapolis street names
STREETS = ["Oak", "Elm", "Pine", "Maple", "Cedar", "Birch", "Walnut", 
           "Cherry", "Ash", "Willow", "Spruce", "Poplar"]
TYPES = ["St", "Ave", "Dr", "Ln", "Way", "Ct", "Blvd"]

NEIGHBORHOODS = [
    "Downtown", "Broad Ripple", "Fountain Square", 
    "Irvington", "Butler-Tarkington", "Carmel", "Fishers"
]

def generate_unique_address():
    """Generate address that's NOT in RAG system"""
    number = random.randint(100, 9999)
    street = random.choice(STREETS)
    street_type = random.choice(TYPES)
    return f"{number} {street} {street_type}, Indianapolis, IN"


def create_leads(count=100):
    """Create leads with DIFFERENT addresses than RAG"""
    
    print(f"🏠 Creating {count} leads with unique addresses...\n")
    
    # Clear existing leads
    from database import SessionLocal
    
    db = SessionLocal()
    db.query(Lead).delete()
    db.commit()
    db.close()
    
    # Names
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    
    # Create your test numbers with specific addresses
    # These are NOT in RAG, so RAG will estimate
    
    print("Creating your test leads:")
    add_lead(
        "+18123224878", 
        "456 Oak Street, Indianapolis, IN",  # NOT in RAG
        "Prajwal Venugopal"
    )
    print(f"✅ +18123224878 → 456 Oak Street (NOT in RAG)")
    
    add_lead(
        "+18123225617",
        "789 Elm Avenue, Indianapolis, IN",  # NOT in RAG
        "Test User"
    )
    print(f"✅ +18123225617 → 789 Elm Avenue (NOT in RAG)")
    
    # Generate rest
    print(f"\nGenerating {count-2} more leads...")
    
    for i in range(2, count):
        phone = f"+1812555{1000 + i:04d}"
        address = generate_unique_address()
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        add_lead(phone, address, name)
        
        if (i + 1) % 20 == 0:
            print(f"  Added {i + 1} leads...")
    
    print(f"\n✅ Created {count} leads")
    print(f"\n⚠️  IMPORTANT: These addresses are NOT in ChromaDB")
    print(f"   So RAG will search for SIMILAR properties and estimate")


if __name__ == "__main__":
    create_leads(100)