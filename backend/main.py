from fastapi import FastAPI, Form
from fastapi.responses import Response
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize OpenAI with LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Store active conversations
# Key = phone number, Value = list of messages (conversation history)
active_conversations = {}


def get_conversation_history(phone_number: str):
    """
    Get or create conversation history for this phone number
    """
    if phone_number not in active_conversations:
        active_conversations[phone_number] = []
        print(f"✅ Created new conversation for {phone_number}")
    
    return active_conversations[phone_number]


def get_ai_response(phone_number: str, user_input: str) -> str:
    """
    Generate AI response with full conversation history
    """
    # Get conversation history
    history = get_conversation_history(phone_number)
    
    # Create the prompt
    system_message = """You are Vanessa, a friendly real estate acquisitions assistant calling homeowners.

Your goal: Determine if they're interested in selling their property in under 90 seconds.

Personality:
- Warm and conversational (not robotic)
- Professional but friendly
- Keep responses under 25 words
- Ask ONE question at a time

Conversation flow:
1. Confirm they're the property owner
2. Ask if they've considered selling
3. If interested → ask about price range and timeline
4. If not interested → thank them politely and say goodbye

Rules:
- Use natural speech (contractions like "you're", "I'm")
- Never repeat questions you already asked
- Remember what they told you
- If they say no/not interested → end politely with "Thanks for your time, have a great day!"
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


@app.get("/")
async def home():
    return {
        "status": "Vanessa AI is online!",
        "version": "3.0 - Now with Memory!",
        "active_calls": len(active_conversations)
    }


@app.post("/voice/incoming")
async def handle_incoming_call(From: str = Form(None)):
    """
    Initial greeting when call starts
    """
    print(f"📞 New call from: {From}")
    
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
    CallStatus: str = Form(None)
):
    """
    Process caller's response with memory
    """
    print(f"💬 {From} said: {SpeechResult}")
    
    # Check if call ended
    if CallStatus == "completed":
        cleanup_conversation(From)
        return Response(content="", media_type="text/xml")
    
    # Generate response with full conversation history
    ai_response = get_ai_response(From, SpeechResult)
    
    print(f"🤖 Vanessa responds: {ai_response}")
    
    # Check if conversation should end
    should_end = check_if_should_end(SpeechResult, ai_response)
    
    if should_end:
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


def check_if_should_end(user_input: str, ai_response: str) -> bool:
    """
    Simple logic to detect if call should end
    """
    end_phrases = [
        "not interested",
        "don't call",
        "remove me",
        "stop calling",
        "no thanks",
        "goodbye",
        "have a great day"
    ]
    
    combined = (user_input + " " + ai_response).lower()
    
    return any(phrase in combined for phrase in end_phrases)


def cleanup_conversation(phone_number: str):
    """
    Remove conversation from memory when call ends
    """
    if phone_number in active_conversations:
        del active_conversations[phone_number]
        print(f"🧹 Cleaned up conversation for {phone_number}")


@app.get("/active-calls")
async def get_active_calls():
    """
    Debug endpoint to see active conversations
    """
    return {
        "active_calls": list(active_conversations.keys()),
        "count": len(active_conversations)
    }


@app.get("/conversation/{phone_number}")
async def get_conversation(phone_number: str):
    """
    Debug endpoint to see a specific conversation history
    """
    if phone_number in active_conversations:
        history = active_conversations[phone_number]
        formatted = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted.append({"role": "assistant", "content": msg.content})
        return {"phone": phone_number, "history": formatted}
    else:
        return {"error": "No active conversation for this number"}