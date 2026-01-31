"""
Intent classification using trained DistilBERT model
"""

from transformers import pipeline
import json
import os

# Load label mapping
LABEL_MAPPING_PATH = './models/intent_classifier/label_mapping.json'

# Global classifier (loaded once at startup)
_classifier = None
_label_names = None


def load_intent_classifier():
    """Load the trained model at server startup"""
    global _classifier, _label_names
    
    if _classifier is None:
        try:
            print("🤖 Loading intent classification model...")
            
            # Load the trained model
            _classifier = pipeline(
                'text-classification',
                model='./models/intent_classifier',
                device=-1  # -1 = CPU, 0 = GPU
            )
            
            # Load label mapping
            with open(LABEL_MAPPING_PATH, 'r') as f:
                labels = json.load(f)
                _label_names = {v: k for k, v in labels.items()}
            
            print("✅ Intent classifier loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading intent classifier: {e}")
            print("⚠️  Falling back to keyword-based classification")
            _classifier = None
    
    return _classifier is not None


def classify_intent_ml(conversation_text: str):
    """
    Classify intent using trained ML model
    
    Args:
        conversation_text: Full conversation or latest user message
        
    Returns:
        dict: {'intent': str, 'confidence': float, 'method': str}
    """
    global _classifier, _label_names
    
    if _classifier is None:
        return classify_intent_keyword(conversation_text)
    
    try:
        # Get prediction from model
        result = _classifier(conversation_text)[0]
        
        # Extract label and confidence
        label_id = int(result['label'].split('_')[-1])
        intent = _label_names.get(label_id, "UNKNOWN")
        confidence = result['score']
        
        return {
            'intent': intent,
            'confidence': confidence,
            'method': 'ml_model'
        }
        
    except Exception as e:
        print(f"❌ ML classification failed: {e}")
        return classify_intent_keyword(conversation_text)


def classify_intent_keyword(conversation_text: str):
    """
    Fallback: Keyword-based classification
    """
    text_lower = conversation_text.lower()
    
    # NOT_INTERESTED signals
    if any(word in text_lower for word in ['no', 'not interested', 'remove', 'stop calling', "don't call"]):
        return {'intent': 'NOT_INTERESTED', 'confidence': 0.8, 'method': 'keyword'}
    
    # QUALIFIED signals (has both price and timeline)
    has_price = any(word in text_lower for word in ['$', 'k', '000', 'hundred', 'thousand', 'million'])
    has_timeline = any(word in text_lower for word in ['month', 'week', 'asap', 'soon', 'immediately', 'year'])
    
    if has_price and has_timeline:
        return {'intent': 'QUALIFIED', 'confidence': 0.7, 'method': 'keyword'}
    
    # EXPLORING signals
    if any(word in text_lower for word in ['how', 'what', 'tell me', 'explain', 'information', 'curious']):
        return {'intent': 'EXPLORING', 'confidence': 0.6, 'method': 'keyword'}
    
    # INTERESTED signals
    if any(word in text_lower for word in ['yes', 'interested', 'considering', 'maybe', 'thinking about']):
        return {'intent': 'INTERESTED', 'confidence': 0.6, 'method': 'keyword'}
    
    # Default
    return {'intent': 'EXPLORING', 'confidence': 0.5, 'method': 'keyword'}


def get_intent_from_conversation(phone_number: str, latest_message: str):
    """
    Classify intent from conversation
    
    Args:
        phone_number: Caller's phone number
        latest_message: Most recent user message
        
    Returns:
        dict: Intent classification result
    """
    # For now, just use the latest message
    # Could expand to use full conversation history
    
    return classify_intent_ml(latest_message)