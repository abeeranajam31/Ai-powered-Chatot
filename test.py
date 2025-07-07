# test_tavily.py
import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

# Load environment variables
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate API key
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in the environment.")

# Initialize Tavily tool
tavily_tool = TavilySearch(max_results=3)

@tool
def tavily_search(query: str) -> str:
    """Search the web for real-time or recent information."""
    try:
        results = tavily_tool.invoke({"query": query})
        return str(results)
    except Exception as e:
        return f"Tavily search failed: {str(e)}"

# Test the Tavily tool
def test_tavily():
    test_queries = [
        "What's the weather like in Lahore, Pakistan today?",
        "Recent news about artificial intelligence",
        "Current stock market trends"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = tavily_search(query)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_tavily()