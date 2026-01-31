"""
MongoDB connection and operations for storing full conversation transcripts
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.vanessa_ai  # Database name
transcripts_collection = db.transcripts  # Collection name


async def save_transcript_to_mongo(
    call_sid: str,
    phone_number: str,
    conversation_history: list,
    intent: str,
    metadata: dict = None
):
    """
    Save full conversation transcript to MongoDB
    
    Args:
        call_sid: Twilio call ID
        phone_number: Caller's phone
        conversation_history: List of HumanMessage/AIMessage objects
        intent: Classified intent (INTERESTED, QUALIFIED, etc.)
        metadata: Additional data (price, timeline, duration, etc.)
    """
    
    # Convert LangChain messages to dict format
    turns = []
    for i, msg in enumerate(conversation_history):
        turn = {
            "turn_number": i + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": "caller" if msg.type == "human" else "vanessa",
            "message": msg.content
        }
        turns.append(turn)
    
    # Build document
    document = {
        "call_sid": call_sid,
        "phone_number": phone_number,
        "intent": intent,
        "turns": turns,
        "metadata": metadata or {},
        "created_at": datetime.utcnow()
    }
    
    try:
        result = await transcripts_collection.insert_one(document)
        print(f"💾 Saved transcript to MongoDB: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return None


async def get_recent_transcripts(limit: int = 10):
    """
    Get recent conversation transcripts
    """
    try:
        cursor = transcripts_collection.find().sort("created_at", -1).limit(limit)
        transcripts = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for transcript in transcripts:
            transcript["_id"] = str(transcript["_id"])
            transcript["created_at"] = transcript["created_at"].isoformat()
        
        return transcripts
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return []


async def get_transcript_by_call_sid(call_sid: str):
    """
    Get a specific conversation transcript
    """
    try:
        transcript = await transcripts_collection.find_one({"call_sid": call_sid})
        
        if transcript:
            transcript["_id"] = str(transcript["_id"])
            transcript["created_at"] = transcript["created_at"].isoformat()
        
        return transcript
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return None