import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily client safely
api_key = os.getenv("TAVILY_API_KEY")
tavily_client = None
if api_key:
    try:
        tavily_client = TavilyClient(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Tavily: {e}")

def search_web(query: str, include_raw_content: bool = False) -> str:
    """
    Wrapper for Tavily search with a fallback if it fails or isn't configured.
    Always uses basic search to conserve credits.
    """
    if not tavily_client:
        return ""
        
    try:
        response = tavily_client.search(
            query=query, 
            search_depth="basic",
            include_raw_content=include_raw_content
        )
        
        # Format the response into a readable string
        results = []
        for item in response.get("results", []):
            title = item.get("title", "")
            content = item.get("content", "")
            raw = item.get("raw_content", "")
            
            result_str = f"Title: {title}\nSummary: {content}"
            if include_raw_content and raw:
                result_str += f"\nRaw Content Snippet: {raw[:500]}..."
            
            results.append(result_str)
            
        return "\n\n".join(results)
    except Exception as e:
        print(f"Tavily search failed for query '{query}': {e}")
        return ""
