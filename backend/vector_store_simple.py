"""
Simple vector search using OpenAI embeddings + cosine similarity
No external vector DB needed!
"""
import os
import json
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load properties
with open('properties.json', 'r') as f:
    data = json.load(f)
    PROPERTIES = data['properties'][:500]  # Get first 500

# Cache embeddings
EMBEDDINGS_CACHE = {}

def get_embedding(text: str):
    """Get embedding from OpenAI"""
    if text in EMBEDDINGS_CACHE:
        return EMBEDDINGS_CACHE[text]
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embedding = response.data[0].embedding
    EMBEDDINGS_CACHE[text] = embedding
    return embedding

def search_properties(query: str, k: int = 5):
    """Search properties using semantic similarity"""
    print(f"Searching for: {query}")
    
    # Get query embedding
    query_embedding = get_embedding(query)
    
    # Calculate similarity with all properties (only first 20 for speed)
    similarities = []
    for prop in PROPERTIES[:20]:  # Limit to first 20 for demo
        prop_text = f"{prop['address']} in {prop.get('neighborhood', 'Columbus')}, ${prop['assessed_value']:,}, built {prop['year_built']}"
        prop_embedding = get_embedding(prop_text)
        
        # Cosine similarity
        sim = cosine_similarity(
            [query_embedding],
            [prop_embedding]
        )[0][0]
        
        similarities.append((sim, prop))
    
    # Sort by similarity and return top k
    similarities.sort(reverse=True, key=lambda x: x[0])
    results = [prop for _, prop in similarities[:k]]
    
    print(f"✅ Found {len(results)} properties")
    return results

# Test
if __name__ == "__main__":
    print(f"Loaded {len(PROPERTIES)} properties")
    print("Testing property search...")
    results = search_properties("property in downtown", k=3)
    for prop in results:
        print(f"  - {prop['address']}: ${prop['assessed_value']:,} ({prop['neighborhood']})")
    print("✅ Done!")
