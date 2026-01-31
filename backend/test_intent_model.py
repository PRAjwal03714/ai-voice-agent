"""
Test the intent classification model
"""

from intent_classifier import load_intent_classifier, classify_intent_ml

# Load model
print("Loading model...")
load_intent_classifier()
print()

# Test examples
test_cases = [
    "Yes I want to sell for 500K in 3 months",
    "Maybe, just looking at options",
    "No I'm not interested",
    "Tell me more about the process",
    "I'm considering selling but not sure about timing",
    "Stop calling me",
    "What's my property worth?",
    "I want to sell ASAP for around 400K"
]

print("🧪 Testing Intent Classification")
print("=" * 60)

for text in test_cases:
    result = classify_intent_ml(text)
    print(f"\nInput: '{text}'")
    print(f"  Intent: {result['intent']}")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"  Method: {result['method']}")

print("\n" + "=" * 60)