from vector_store_simple import search_properties
from fastapi import FastAPI, Form
from fastapi.responses import Response
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv
import time
from fastapi.middleware.cors import CORSMiddleware

from rag_system import get_property_context
from database import save_call_data
from mongodb import save_transcript_to_mongo, get_recent_transcripts, get_transcript_by_call_sid
from lead_database import get_property_for_phone
from intent_classifier_openai import classify_intent  #  load_intent_classifier, get_intent_from_conversation

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup

# Initialize OpenAI with LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Store active conversations
active_conversations = {}


# Load model at startup
@app.on_event("startup")
async def startup_event():
    """Load ML model when server starts"""
    print("🚀 Starting up Vanessa AI...")
    #load_intent_classifier()  # Removed - using OpenAI now
    print("✅ Startup complete!")


def get_conversation_history(phone_number: str):
    """Get or create conversation history for this phone number"""
    if phone_number not in active_conversations:
        active_conversations[phone_number] = {
            "messages": [],
            "start_time": time.time(),
            "call_sid": None
        }
        print(f"✅ Created new conversation for {phone_number}")
    
    return active_conversations[phone_number]["messages"]


def get_ai_response(phone_number: str, user_input: str) -> str:
    """Generate AI response with property context"""
    history = get_conversation_history(phone_number)
    
    # Look up which property this caller owns
    caller_address = get_property_for_phone(phone_number)
    if caller_address:
        print(f"📍 Caller owns: {caller_address}")
    
    # Get property context with the caller's specific address
    property_context = get_property_context(user_input)
    
    # Create the system prompt WITH property context
    system_message = f"""You are Vanessa, a friendly real estate acquisitions assistant calling homeowners.

Your goal: Determine if they're interested in selling their property in under 90 seconds.

{property_context}

Personality:
- Warm and conversational (not robotic)
- Professional but friendly
- Keep responses under 35 words
- Ask ONE question at a time
- When you have property information, USE IT to give specific, helpful answers

Conversation flow:
1. Confirm they're the property owner
2. Ask if they've considered selling
3. If interested → ask about price range (use property data to guide them!)
4. Ask about timeline
5. AFTER getting timeline → ALWAYS end with "Thanks for your time, have a great day!"

Rules:
- Use natural speech (contractions like "you're", "I'm")
- Never repeat questions you already asked
- Remember what they told you
- If you have property value data, mention it naturally when discussing price
- CRITICAL: After the user tells you their timeline, you MUST end the call by saying "Thanks for your time, have a great day!"
- If they say no/not interested → end with "No problem! Thanks for your time, have a great day!"
"""
    
    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_message}]
    
    # Add conversation history
    for msg in history:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    # Get response from LLM
    response = llm.invoke(messages)
    ai_text = response.content
    
    # Store in history
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=ai_text))
    
    return ai_text


def extract_price(text: str) -> str:
    """Extract price from conversation text"""
    text_lower = text.lower()
    
    if "500" in text_lower or "500k" in text_lower:
        return "500K"
    elif "400" in text_lower or "400k" in text_lower:
        return "400K"
    elif "300" in text_lower or "300k" in text_lower:
        return "300K"
    elif "600" in text_lower or "600k" in text_lower:
        return "600K"
    elif "700" in text_lower or "700k" in text_lower:
        return "700K"
    elif "800" in text_lower or "800k" in text_lower:
        return "800K"
    
    return None


def extract_timeline(text: str) -> str:
    """Extract timeline from conversation text"""
    text_lower = text.lower()
    
    if "asap" in text_lower or "soon as possible" in text_lower or "immediately" in text_lower:
        return "ASAP"
    elif "month" in text_lower and "3" in text_lower:
        return "3-6 months"
    elif "month" in text_lower:
        return "Few months"
    elif "year" in text_lower:
        return "1+ year"
    elif "exploring" in text_lower or "just looking" in text_lower:
        return "Exploring"
    
    return None


@app.get("/")
async def home():
    return {
        "status": "Vanessa AI is online!",
        "version": "4.0 - With ML Intent Classification!",
        "active_calls": len(active_conversations)
    }


@app.post("/voice/incoming")
async def handle_incoming_call(From: str = Form(None), CallSid: str = Form(None)):
    """Initial greeting when call starts"""
    print(f"📞 New call from: {From} (SID: {CallSid})")
    
    # Store call SID
    if From not in active_conversations:
        active_conversations[From] = {
            "messages": [],
            "start_time": time.time(),
            "call_sid": CallSid
        }
    else:
        active_conversations[From]["call_sid"] = CallSid
    
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/voice/process" speechTimeout="auto" language="en-US">
        <Say voice="Polly.Joanna">
            Hi, this is Vanessa from HomeConnect. Are you the property owner?
        </Say>
    </Gather>
</Response>
"""
    
    return Response(content=twiml, media_type="text/xml")


@app.post("/voice/process")
async def process_speech(
    SpeechResult: str = Form(None),
    From: str = Form(None),
    CallStatus: str = Form(None),
    CallSid: str = Form(None)
):
    """Process caller's response with ML intent classification"""
    print(f"💬 {From} said: {SpeechResult}")
    
    # Check if call ended
    if CallStatus == "completed":
        cleanup_conversation(From)
        return Response(content="", media_type="text/xml")
    
    # Generate response with full conversation history
    ai_response = get_ai_response(From, SpeechResult)
    
    print(f"🤖 Vanessa responds: {ai_response}")
    
    # NEW: Classify intent using ML model
    should_end, intent_data = should_end_call(From, SpeechResult)
    
    # Log intent classification
    print(f"📊 Intent: {intent_data['intent']} "
          f"(confidence: {intent_data['confidence']:.1%}, "
          f"(confidence: {intent_data['confidence']:.1%})")
    
    # Check if conversation should end
    if should_end or check_if_should_end(SpeechResult, ai_response):
        # Save call to database before ending
        await save_call_data(From, CallSid, intent_data)
        
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{ai_response}</Say>
    <Hangup/>
</Response>
"""
        cleanup_conversation(From)
    else:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/voice/process" speechTimeout="auto" language="en-US">
        <Say voice="Polly.Joanna">{ai_response}</Say>
    </Gather>
</Response>
"""
    
    return Response(content=twiml, media_type="text/xml")


def should_end_call(phone_number: str, user_input: str) -> tuple[bool, dict]:
    """
    Determine if call should end and extract intent using ML model
    
    Returns:
        tuple: (should_end: bool, intent_data: dict)
    """
    # Classify intent using ML model
    intent_result = classify_intent(user_input)
    
    intent = intent_result['intent']
    
    # End call if NOT_INTERESTED or if we have enough info (QUALIFIED)
    should_end = intent in ['NOT_INTERESTED']
    
    return should_end, intent_result


async def save_call_data(phone_number: str, call_sid: str, intent_data: dict):
    """Extract data from conversation and save to BOTH databases"""
    if phone_number not in active_conversations:
        return
    
    conversation_data = active_conversations[phone_number]
    history = conversation_data["messages"]
    start_time = conversation_data["start_time"]
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Build full transcript
    transcript_parts = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            transcript_parts.append(f"Caller: {msg.content}")
        elif isinstance(msg, AIMessage):
            transcript_parts.append(f"Vanessa: {msg.content}")
    
    full_transcript = "\n".join(transcript_parts)
    
    # Extract information
    price = extract_price(full_transcript)
    timeline = extract_timeline(full_transcript)
    intent = intent_data['intent']
    
    # Import with alias to avoid name collision
    from database import save_call_data as save_to_db
    
    # Save to PostgreSQL
    # save_to_db(
    #     phone_number=phone_number,
    #     call_sid=call_sid or "UNKNOWN",
    #     intent=intent,
    #     confidence=intent_data.get('confidence', 0.0)
    # )
    save_to_db(
    phone_number=phone_number,
    call_sid=call_sid or "UNKNOWN",
    intent=intent,
    confidence=intent_data.get('confidence', 0.0),
    price_mentioned=price,
    timeline_mentioned=timeline,
    call_duration=round(duration, 2)
)

    
    # Save to MongoDB (full transcript)
    await save_transcript_to_mongo(
        call_sid=call_sid or "UNKNOWN",
        phone_number=phone_number,
        conversation_history=history,
        intent=intent,
        metadata={
            "price_mentioned": price,
            "timeline_mentioned": timeline,
            "call_duration": round(duration, 2),
            "total_turns": len(history),
            "ml_confidence": intent_data.get('confidence', 0),
            "classification_method": intent_data.get('method', 'unknown')
        }
    )

def check_if_should_end(user_input: str, ai_response: str) -> bool:
    """Detect if call should end based on conversation phrases"""
    end_phrases = [
        "not interested",
        "don't call",
        "remove me",
        "stop calling",
        "no thanks",
        "goodbye",
        "have a great day",
        "bye",
        "thanks for your time",
        "thank you for your time"
    ]
    
    combined = (user_input + " " + ai_response).lower()
    
    return any(phrase in combined for phrase in end_phrases)


def cleanup_conversation(phone_number: str):
    """Remove conversation from memory when call ends"""
    if phone_number in active_conversations:
        del active_conversations[phone_number]
        print(f"🧹 Cleaned up conversation for {phone_number}")


@app.get("/active-calls")
async def get_active_calls():
    """Debug endpoint to see active conversations"""
    return {
        "active_calls": list(active_conversations.keys()),
        "count": len(active_conversations)
    }


@app.get("/api/transcripts")
async def get_transcripts(limit: int = 10):
    """Get recent full conversation transcripts from MongoDB"""
    transcripts = await get_recent_transcripts(limit)
    return {"transcripts": transcripts, "count": len(transcripts)}


@app.get("/api/transcript/{call_sid}")
async def get_transcript(call_sid: str):
    """Get a specific conversation transcript"""
    transcript = await get_transcript_by_call_sid(call_sid)
    
    if transcript:
        return transcript
    else:
        return {"error": "Transcript not found"}


@app.get("/conversation/{phone_number}")
async def get_conversation(phone_number: str):
    """Debug endpoint to see a specific conversation history"""
    if phone_number in active_conversations:
        conversation_data = active_conversations[phone_number]
        history = conversation_data["messages"]
        formatted = []
        
        for msg in history:
            if isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted.append({"role": "assistant", "content": msg.content})
        
        return {
            "phone": phone_number,
            "call_sid": conversation_data.get("call_sid"),
            "duration": round(time.time() - conversation_data["start_time"], 2),
            "history": formatted
        }
    else:
        return {"error": "No active conversation for this number"}


@app.get("/recent-calls")
async def get_recent_calls():
    """Get recent calls from database"""
    from database import SessionLocal, CallLog
    
    db = SessionLocal()
    try:
        calls = db.query(CallLog).order_by(CallLog.created_at.desc()).limit(10).all()
        
        result = []
        for call in calls:
            result.append({
                "id": call.id,
                "phone_number": call.phone_number,  # ← Make sure this exists
                "phone": call.phone_number,         # ← Add alias just in case
                "intent": call.intent,
                "price_mentioned": call.price_mentioned,
                "price": call.price_mentioned,      # ← Add alias
                "timeline_mentioned": call.timeline_mentioned,
                "timeline": call.timeline_mentioned, # ← Add alias
                "call_duration": call.call_duration if call.call_duration else 0,
                "duration": call.call_duration if call.call_duration else 0,
                "created_at": call.created_at.isoformat() if call.created_at else ""
            })
        
        return {"calls": result, "count": len(result)}
    except Exception as e:
        print(f"❌ Error in /recent-calls: {e}")
        return {"calls": [], "count": 0}
    finally:
        db.close()


@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics for the dashboard"""
    from database import SessionLocal, CallLog
    
    db = SessionLocal()
    try:
        calls = db.query(CallLog).all()
        
        if not calls:
            return {
                "total_calls": 0,
                "qualified_leads": 0,
                "avg_duration": 0,
                "intent_distribution": {
                    "QUALIFIED": 0,
                    "INTERESTED": 0,
                    "NOT_INTERESTED": 0,
                    "EXPLORING": 0
                }
            }
        
        total_calls = len(calls)
        qualified = len([c for c in calls if c.intent == 'QUALIFIED'])
        avg_duration = sum(c.call_duration for c in calls) / total_calls if total_calls > 0 else 0
        
        intent_dist = {}
        for call in calls:
            intent = call.intent or "UNKNOWN"
            intent_dist[intent] = intent_dist.get(intent, 0) + 1
        
        return {
            "total_calls": total_calls,
            "qualified_leads": qualified,
            "avg_duration": round(avg_duration, 2),
            "intent_distribution": intent_dist
        }
    except Exception as e:
        print(f"❌ Error in /api/stats: {e}")
        return {
            "total_calls": 0,
            "qualified_leads": 0,
            "avg_duration": 0,
            "intent_distribution": {}
        }
    finally:
        db.close()

@app.get("/api/export/csv")
async def export_calls_csv():
    """Export all calls as CSV for BI tools"""
    from database import SessionLocal, CallLog
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    db = SessionLocal()
    try:
        calls = db.query(CallLog).order_by(CallLog.created_at.desc()).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'id', 'phone_number', 'call_sid', 'intent', 
            'price_mentioned', 'timeline_mentioned', 'call_duration', 
            'created_at', 'date', 'time'
        ])
        
        # Data rows
        for call in calls:
            created_at = call.created_at.strftime('%Y-%m-%d %H:%M:%S') if call.created_at else ''
            date_only = call.created_at.strftime('%Y-%m-%d') if call.created_at else ''
            time_only = call.created_at.strftime('%H:%M:%S') if call.created_at else ''
            
            writer.writerow([
                call.id,
                call.phone_number,
                call.call_sid,
                call.intent,
                call.price_mentioned or '',
                call.timeline_mentioned or '',
                call.call_duration if call.call_duration else 0,
                created_at,
                date_only,
                time_only
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=vanessa_calls.csv"}
        )
        
    finally:
        db.close()


@app.get("/api/export/json")
async def export_calls_json():
    """Export all calls as JSON for BI tools"""
    from database import SessionLocal, CallLog
    
    db = SessionLocal()
    try:
        calls = db.query(CallLog).order_by(CallLog.created_at.desc()).all()
        
        result = []
        for call in calls:
            result.append({
                "id": call.id,
                "phone_number": call.phone_number,
                "call_sid": call.call_sid,
                "intent": call.intent,
                "price_mentioned": call.price_mentioned,
                "timeline_mentioned": call.timeline_mentioned,
                "call_duration": call.call_duration if call.call_duration else 0,
                "created_at": call.created_at.isoformat() if call.created_at else None,
                "date": call.created_at.strftime('%Y-%m-%d') if call.created_at else None,
                "time": call.created_at.strftime('%H:%M:%S') if call.created_at else None,
            })
        
        return {
            "total_calls": len(result),
            "calls": result
        }
        
    finally:
        db.close()


@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get summary statistics for BI dashboards"""
    from database import SessionLocal, CallLog
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Total calls
        total_calls = db.query(func.count(CallLog.id)).scalar()
        
        # Calls by intent
        intent_breakdown = db.query(
            CallLog.intent,
            func.count(CallLog.id).label('count')
        ).group_by(CallLog.intent).all()
        
        # Average duration
        avg_duration = db.query(func.avg(CallLog.call_duration)).scalar() or 0
        
        # Qualified leads
        qualified = db.query(func.count(CallLog.id)).filter(
            CallLog.intent == 'QUALIFIED'
        ).scalar()
        
        # Conversion rate
        conversion_rate = (qualified / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "qualified_leads": qualified,
            "conversion_rate": round(conversion_rate, 2),
            "avg_duration": round(avg_duration, 2),
            "intent_breakdown": {
                intent: count for intent, count in intent_breakdown
            }
        }
        
    finally:
        db.close()
@app.get("/cors-test")
async def cors_test():
    return {"ok": True}
