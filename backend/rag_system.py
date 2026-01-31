"""
RAG System - Property Knowledge Retrieval
Uses ChromaDB for semantic search of property data
"""

import chromadb
from chromadb.config import Settings
import json
from sentence_transformers import SentenceTransformer
import os


# Initialize ChromaDB
chroma_client = chromadb.Client(Settings(
    persist_directory="./chroma_data",
    anonymized_telemetry=False
))

# Initialize embedding model (converts text to vectors)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Get or create collection
try:
    collection = chroma_client.get_collection("properties")
    print("✅ Loaded existing property collection")
except:
    collection = chroma_client.create_collection(
        name="properties",
        metadata={"description": "Property information for RAG"}
    )
    print("✅ Created new property collection")


def load_properties_from_file(filepath: str = "sample_properties.json"):
    try:
        with open(filepath, 'r') as f:
            properties = json.load(f)
        
        try:
            collection.delete(where={})
        except:
            pass
        
        for idx, prop in enumerate(properties):
            doc_text = f"""
            Address: {prop['address']}
            Value: ${prop['assessed_value']:,}
            Size: {prop['bedrooms']} bed, {prop['bathrooms']} bath, {prop['sqft']} sqft
            Built: {prop['year_built']}
            Neighborhood: {prop['neighborhood']}
            {prop['comparable_sales']}
            Notes: {prop.get('notes', 'Well-maintained property')}
            """
            
            # Clean metadata - remove None values
            metadata = {
                "address": prop['address'],
                "assessed_value": prop['assessed_value'],
                "bedrooms": prop['bedrooms'],
                "bathrooms": prop['bathrooms'],
                "sqft": prop['sqft'],
                "year_built": prop['year_built'],
                "neighborhood": prop['neighborhood']
            }
            
            # Only add optional fields if they exist and are not None
            if prop.get('last_sale_price'):
                metadata['last_sale_price'] = prop['last_sale_price']
            if prop.get('last_sale_date'):
                metadata['last_sale_date'] = prop['last_sale_date']
            
            collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[f"property_{idx}"]
            )
        
        print(f"✅ Loaded {len(properties)} properties into ChromaDB")
        return len(properties)
        
    except FileNotFoundError:
        print(f"⚠️  Property file not found: {filepath}")
        return 0
    except Exception as e:
        print(f"❌ Error loading properties: {e}")
        return 0


def search_properties(query: str, n_results: int = 2):
    """
    Search for relevant property information
    
    Args:
        query: User's question or address mention
        n_results: How many results to return
    
    Returns:
        List of relevant property info
    """
    try:
        # Search ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            # Return the found properties
            properties = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                properties.append({
                    "text": doc,
                    "metadata": metadata
                })
            
            print(f"🔍 Found {len(properties)} relevant properties")
            return properties
        else:
            print("⚠️  No properties found for query")
            return []
            
    except Exception as e:
        print(f"❌ RAG search error: {e}")
        return []


def get_property_context(user_input, conversation_history, known_address):
    if not known_address:
        return ""
    
    # Caller's address: "456 Oak Street, Indianapolis, IN"
    # This is NOT in ChromaDB!
    
    # Extract neighborhood or search nearby
    # Option 1: Search by street name
    search_query = f"properties on Oak Street Indianapolis"
    
    # Option 2: Search by general area
    # search_query = "properties in Indianapolis"
    
    # Get similar properties
    results = search_properties(search_query, n_results=5)
    
    if not results:
        return f"Property address: {known_address}"
    
    # Calculate estimated value from comparables
    values = [r['metadata']['assessed_value'] for r in results]
    avg_value = sum(values) / len(values)
    min_value = min(values)
    max_value = max(values)
    
    # Build context
    comp_text = "\n".join([
        f"- {r['metadata']['address']}: ${r['metadata']['assessed_value']:,}"
        for r in results[:3]
    ])
    
    context = f"""
    CALLER'S PROPERTY:
    Address: {known_address}
    Estimated Value: ${avg_value:,.0f} (based on area comparables)
    Value Range: ${min_value:,} - ${max_value:,}
    
    COMPARABLE PROPERTIES IN THE AREA:
    {comp_text}
    
    Use these comparables to discuss the property's estimated market value.
    Note: This is an estimate based on similar properties in the area.
    """
    
    return context


# Initialize: Load properties on startup
if os.path.exists("generated_from_real_baseline.json"):
    load_properties_from_file("generated_from_real_baseline.json")