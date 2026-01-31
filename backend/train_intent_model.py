"""
Train intent classification model
Fine-tunes DistilBERT on conversation data
"""

from transformers import (
    DistilBertTokenizer, 
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import torch
from torch.utils.data import Dataset
import json
import numpy as np

# Label mapping
LABELS = {
    "NOT_INTERESTED": 0,
    "EXPLORING": 1,
    "INTERESTED": 2,
    "QUALIFIED": 3
}

LABEL_NAMES = {v: k for k, v in LABELS.items()}


class IntentDataset(Dataset):
    """PyTorch Dataset for intent classification"""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def compute_metrics(pred):
    """Calculate evaluation metrics"""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted'
    )
    acc = accuracy_score(labels, preds)
    
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


def train_intent_model():
    """Main training function"""
    
    print("="*60)
    print("INTENT CLASSIFICATION MODEL TRAINING")
    print("="*60)
    print()
    
    # Load training data
    print("📊 Loading training data...")
    with open('intent_training_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} examples")
    
    # Prepare data
    texts = [item['text'] for item in data]
    labels = [LABELS[item['label']] for item in data]
    
    # Split train/test (80/20)
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"📚 Train: {len(train_texts)} examples")
    print(f"📝 Test: {len(test_texts)} examples")
    
    # Initialize tokenizer and model
    print("\n🔧 Loading DistilBERT from Hugging Face...")
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=len(LABELS)
    )
    
    print("✅ Model loaded")
    
    # Create datasets
    print("\n🔄 Preparing datasets...")
    train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
    test_dataset = IntentDataset(test_texts, test_labels, tokenizer)
    
    # Training configuration
    training_args = TrainingArguments(
        output_dir='./intent_model_checkpoints',
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics
    )
    
    # Train!
    print("\n🏋️  Training model (this will take 3-5 minutes)...")
    print("="*60)
    trainer.train()
    
    # Evaluate
    print("\n📈 Evaluating model on test set...")
    results = trainer.evaluate()
    
    # Detailed results
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"\n📊 Test Results:")
    print(f"   Accuracy:  {results['eval_accuracy']:.2%}")
    print(f"   F1 Score:  {results['eval_f1']:.2%}")
    print(f"   Precision: {results['eval_precision']:.2%}")
    print(f"   Recall:    {results['eval_recall']:.2%}")
    
    # Save model
    print("\n💾 Saving model...")
    model.save_pretrained('./models/intent_classifier')
    tokenizer.save_pretrained('./models/intent_classifier')
    
    # Save label mapping
    with open('./models/intent_classifier/label_mapping.json', 'w') as f:
        json.dump(LABELS, f, indent=2)
    
    print("✅ Model saved to ./models/intent_classifier")
    
    # Test predictions
    print("\n🧪 Testing on sample inputs:")
    print("="*60)
    
    from transformers import pipeline
    classifier = pipeline('text-classification', model='./models/intent_classifier')
    
    test_examples = [
        "Yes I want to sell for 500K in 3 months",
        "Maybe, just looking at options",
        "No I'm not interested",
        "Tell me more about the process"
    ]
    
    for text in test_examples:
        result = classifier(text)[0]
        predicted_label = LABEL_NAMES[int(result['label'].split('_')[-1])]
        confidence = result['score']
        print(f"\nInput: '{text}'")
        print(f"   → Prediction: {predicted_label} ({confidence:.1%} confidence)")
    
    print("\n" + "="*60)
    print("🎉 MODEL READY TO USE!")
    print("="*60)
    
    return results


if __name__ == "__main__":
    train_intent_model()