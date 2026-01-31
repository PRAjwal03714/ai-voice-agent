"""
Prepare training data for intent classification model
Exports labeled examples from MongoDB conversations
"""

import json

def create_training_data():
    """
    Create labeled training examples
    In production, you'd export from MongoDB
    For now, we'll create synthetic examples
    """
    
    training_data = [
        # QUALIFIED - Has both price AND timeline
        {"text": "Yes I'm interested. Looking at around 500K and want to sell in the next 3 months.", "label": "QUALIFIED"},
        {"text": "I am the owner. Been thinking about selling for 400K. Timeline is ASAP.", "label": "QUALIFIED"},
        {"text": "Yeah considering it. Property value is about 600K. Need to sell by end of year.", "label": "QUALIFIED"},
        {"text": "I own it. Thinking 450K range. Want to sell within 6 months.", "label": "QUALIFIED"},
        {"text": "Yes that's my property. Around 380K sounds right. Looking to sell soon.", "label": "QUALIFIED"},
        {"text": "I'm the owner. Expecting 520K. Timeline is next few months.", "label": "QUALIFIED"},
        {"text": "Yes interested in selling. Price around 470K. Ready to move in 2 months.", "label": "QUALIFIED"},
        {"text": "That's correct. Value is 410K approximately. Want to close by summer.", "label": "QUALIFIED"},
        {"text": "I am considering it. 550K is what I'm thinking. Timeline flexible but preferably soon.", "label": "QUALIFIED"},
        {"text": "Yes exploring selling. Around 490K market value. Looking at 4-6 month window.", "label": "QUALIFIED"},
        
        # INTERESTED - Considering but no firm details yet
        {"text": "Yes I'm the owner. I've been thinking about selling recently.", "label": "INTERESTED"},
        {"text": "Maybe, I'm considering my options. Not sure about timing yet.", "label": "INTERESTED"},
        {"text": "I am interested but haven't decided on a price.", "label": "INTERESTED"},
        {"text": "Yeah I own it. Thinking about it but no rush.", "label": "INTERESTED"},
        {"text": "Possibly. What do you think it's worth?", "label": "INTERESTED"},
        {"text": "I've thought about selling but not sure when.", "label": "INTERESTED"},
        {"text": "Yes exploring my options. Haven't settled on a number yet.", "label": "INTERESTED"},
        {"text": "Maybe in the future. Still considering.", "label": "INTERESTED"},
        {"text": "I am the owner and open to selling if the price is right.", "label": "INTERESTED"},
        {"text": "Thinking about it. Need to discuss with family first.", "label": "INTERESTED"},
        
        # NOT_INTERESTED - Clear rejection
        {"text": "No I'm not interested in selling.", "label": "NOT_INTERESTED"},
        {"text": "Not right now, thanks.", "label": "NOT_INTERESTED"},
        {"text": "No thanks, not planning to sell.", "label": "NOT_INTERESTED"},
        {"text": "I'm not interested. Please don't call again.", "label": "NOT_INTERESTED"},
        {"text": "No, we're staying here.", "label": "NOT_INTERESTED"},
        {"text": "Not selling. Remove me from your list.", "label": "NOT_INTERESTED"},
        {"text": "No I don't want to sell my property.", "label": "NOT_INTERESTED"},
        {"text": "Not interested at all.", "label": "NOT_INTERESTED"},
        {"text": "No. Stop calling.", "label": "NOT_INTERESTED"},
        {"text": "I'm not planning on selling anytime soon.", "label": "NOT_INTERESTED"},
        
        # EXPLORING - Neutral, gathering info
        {"text": "I'm just looking at my options.", "label": "EXPLORING"},
        {"text": "Tell me more about the process.", "label": "EXPLORING"},
        {"text": "What's the typical timeline for selling?", "label": "EXPLORING"},
        {"text": "I'm curious but not committed yet.", "label": "EXPLORING"},
        {"text": "Just gathering information for now.", "label": "EXPLORING"},
        {"text": "What kind of offer would you make?", "label": "EXPLORING"},
        {"text": "How does this work exactly?", "label": "EXPLORING"},
        {"text": "I'm early in the process of thinking about it.", "label": "EXPLORING"},
        {"text": "Not sure yet, still researching.", "label": "EXPLORING"},
        {"text": "What would be the next steps?", "label": "EXPLORING"},
    ]
    
    # Save to file
    with open('intent_training_data.json', 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"✅ Created {len(training_data)} training examples")
    print(f"💾 Saved to intent_training_data.json")
    
    # Show distribution
    labels = {}
    for item in training_data:
        label = item['label']
        labels[label] = labels.get(label, 0) + 1
    
    print(f"\n📊 Label Distribution:")
    for label, count in labels.items():
        print(f"   {label}: {count} examples")
    
    return training_data


if __name__ == "__main__":
    create_training_data()