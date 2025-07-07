# 🤖 AI-Powered Chatbot with Gemini, LangGraph, and Tavily

An AI-powered chatbot that integrates:
- **Gemini (via LangChain)** for intelligent LLM responses  
- **LangGraph** to manage conversation flow  
- **MongoDB** for session-based chat history  
- **FAISS** for RAG (Retrieval-Augmented Generation)  
- **Tavily** for real-time web search  
- **FastAPI** as the backend  
- **Gradio** (or React) frontend for interaction

---

## 🔧 Features

- ✨ Context-aware LLM responses (via Gemini)
- 🧠 Tool-calling with Tavily for current info (news, weather, etc.)
- 📚 RAG pipeline using FAISS and text-splitter
- 🗂️ MongoDB for storing chat sessions
- ⚡ FastAPI `/chat` endpoint for frontend integration

---

## 💻 Tech Stack

- `langchain-community`
- `langchain-google-genai`
- `langchain-tavily`
- `langgraph`
- `faiss-cpu`
- `PyPDF2`, `langchain-text-splitters`
- `pymongo`, `fastapi`, `uvicorn`
- `gradio` or your frontend
- `python-dotenv`, `tavily-python`, `requests`

---

## 📂 Project Structure

```

chat/
├── lang.py              # Core logic: Gemini + RAG + Tavily + LangGraph
├── main.py              # FastAPI backend
├── .env                 # API keys & Mongo URI
├── requirements.txt     # Dependencies
├── rag\_index/           # FAISS vector store
└── README.md            # Documentation

````

---

## 🚀 Getting Started

### 1. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add `.env` file

Create a `.env` file in the root with the following content:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
MONGO_URI=mongodb://localhost:27017/
```

### 4. Run the FastAPI server

```bash
uvicorn main:app --reload
```

```

---



