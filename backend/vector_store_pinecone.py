"""
Pinecone-based vector store for property search
Using Pinecone v2 API
"""
import os
import pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone (v2 API)
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
)

# Get index
index_name = os.getenv("PINECONE_INDEX", "property-embeddings")

# Initialize embeddings (using OpenAI)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize vector store
vector_store = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings
)

def load_properties_to_pinecone():
    """Load property data into Pinecone"""
    import json
    
    print("Loading properties from properties.json...")
    
    with open('properties.json', 'r') as f:
        properties = json.load(f)
    
    # Prepare documents
    texts = []
    metadatas = []
    
    for prop in properties[:500]:  # Limit to 500
        text = f"{prop['address']} - {prop['bedrooms']} bed, {prop['bathrooms']} bath, ${prop['price']}, {prop['sqft']} sqft"
        texts.append(text)
        metadatas.append({
            "address": prop["address"],
            "price": prop["price"],
            "bedrooms": prop["bedrooms"],
            "bathrooms": prop["bathrooms"],
            "sqft": prop["sqft"]
        })
    
    print(f"Adding {len(texts)} properties to Pinecone...")
    
    # Add to Pinecone in batches
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        vector_store.add_texts(texts=batch_texts, metadatas=batch_metas)
        print(f"  Added batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
    
    print(f"✅ Loaded {len(texts)} properties into Pinecone")

def search_properties(query: str, k: int = 5):
    """Search for properties using natural language"""
    results = vector_store.similarity_search(query, k=k)
    return [doc.metadata for doc in results]

# Load properties on startup
if __name__ == "__main__":
    print("Starting property upload to Pinecone...")
    load_properties_to_pinecone()
    print("✅ Done!")
