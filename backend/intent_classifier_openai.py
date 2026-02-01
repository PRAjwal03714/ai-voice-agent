"""
OpenAI-based intent classification
Replaces local ML model with API calls
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_intent(text: str) -> dict:
    """
    Classify caller intent using OpenAI
    Returns: {"intent": str, "confidence": float}
    """
    
    prompt = f"""Analyze this conversation and classify the caller's intent.

Conversation: "{text}"

Classify into ONE of these categories:
- qualified_buyer: Ready to buy, has financing, specific needs
- interested: Interested but needs more info
- not_interested: Not interested, just browsing
- callback: Wants to be called back later

Respond in this exact format:
Intent: [category]
Confidence: [0.0-1.0]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing real estate sales calls."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        
        # Parse result
        intent = "interested"  # default
        confidence = 0.5
        
        for line in result.split('\n'):
            if 'Intent:' in line:
                intent = line.split('Intent:')[1].strip().lower()
            if 'Confidence:' in line:
                try:
                    confidence = float(line.split('Confidence:')[1].strip())
                except:
                    confidence = 0.5
        
        return {
            "intent": intent,
            "confidence": confidence
        }
    
    except Exception as e:
        print(f"❌ Intent classification error: {e}")
        return {
            "intent": "interested",
            "confidence": 0.5
        }

# Test
if __name__ == "__main__":
    test_text = "I'm looking for a 3 bedroom house under $500k. I have pre-approval ready."
    result = classify_intent(test_text)
    print(f"Intent: {result['intent']}, Confidence: {result['confidence']}")
