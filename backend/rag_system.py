"""
Simple RAG system using lightweight vector search
"""
from vector_store_simple import search_properties

def get_property_context(query: str) -> str:
    """
    Get relevant property context for a query
    """
    try:
        results = search_properties(query, k=3)
        
        if not results:
            return "No properties found matching your criteria."
        
        context = "Here are some properties that match:\n\n"
        for i, prop in enumerate(results, 1):
            context += f"{i}. {prop.get('address', 'Unknown address')}\n"
            context += f"   Value: ${prop.get('assessed_value', 0):,}\n"
            context += f"   Built: {prop.get('year_built', 'Unknown')}\n"
            context += f"   Neighborhood: {prop.get('neighborhood', 'Unknown')}\n\n"
        
        return context
    except Exception as e:
        print(f"❌ Error in get_property_context: {e}")
        return "I'm having trouble searching properties right now."
