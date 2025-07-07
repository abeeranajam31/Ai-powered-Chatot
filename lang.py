import os
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import TypedDict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set.")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set.")

# Tavily setup
tavily_client = TavilySearch(max_results=3)

def tavily_search(query: str) -> str:
    query = query[:400]  # Ensure it doesn't exceed API limit
    print(f"Tavily query: {query} (length: {len(query)})")
    try:
        results = tavily_client.invoke({"query": query})
        return str(results)
    except Exception as e:
        return f"Tavily search failed: {str(e)}"

tavily_tool = Tool(
    name="tavily_search",
    func=tavily_search,
    description="Search the web for real-time or recent information like news, weather, or current events."
)

# Chat model
chat_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
)

# FAISS + embeddings
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.load_local("rag_index", embedding, allow_dangerous_deserialization=True)

# MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["chatbot"]
history_col = db["history"]

def save_message(session_id, role, content):
    history_col.insert_one({"session_id": session_id, "role": role, "content": content})

def get_history(session_id):
    return list(history_col.find({"session_id": session_id}))

def retrieve_context(query):
    docs = vectorstore.similarity_search(query, k=2)
    return "\n".join([doc.page_content for doc in docs])

def rag_tool(state):
    query = state["input"]
    context = retrieve_context(query)
    state["context"] = context
    return state

def chat_node(state):
    user_input = state["input"]
    # Only pass the latest user message, no history
    plain_user_input = user_input.split("User:")[-1].strip()  

    messages = [HumanMessage(content=user_input)]
    try:
        response = chat_model.invoke(messages)
        print(f"Initial response: {response.content}")

        # Check if AI suggests using real-time info
        if any(keyword in response.content.lower() for keyword in ["current", "latest", "today", "now", "real-time"]):
            # Run Tavily on the actual query only
            search_result = tavily_search(plain_user_input)
            messages.append(HumanMessage(content=f"Search results: {search_result}"))
            response = chat_model.invoke(messages)
            print(f"Response after tool call: {response.content}")

        state["output"] = response.content
    except Exception as e:
        state["output"] = f"Error in chat processing: {str(e)}"
    return state

class ChatState(TypedDict):
    input: str
    output: Optional[str]
    context: Optional[str]

graph = StateGraph(state_schema=ChatState)
graph.add_node("input", lambda state: state)
graph.add_node("rag", rag_tool)
graph.add_node("chat", chat_node)
graph.set_entry_point("input")
graph.add_edge("input", "rag")
graph.add_edge("rag", "chat")
graph.add_edge("chat", END)
chat_graph = graph.compile()

def run_chat(session_id, user_input):
    history = get_history(session_id)
    formatted_history = "\n".join(
        f"{'User' if h['role']=='user' else 'AI'}: {h['content']}" for h in history[-6:]
    )
    full_input = f"{formatted_history}\nUser: {user_input}" if formatted_history else f"User: {user_input}"

    state = {"input": full_input}
    try:
        result = chat_graph.invoke(state)
        response = result["output"]
        save_message(session_id, "user", user_input)
        save_message(session_id, "ai", response)
        return response
    except Exception as e:
        return f"Error running chat: {str(e)}"