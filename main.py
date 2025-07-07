from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from lang import run_chat  # uses session_id, formats history, runs LangGraph

app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    session_id = data.get("session_id")
    message = data.get("message")

    if not session_id or not message:
        return {"error": "Missing session_id or message."}

    # Run LangGraph logic with RAG + Tavily + Gemini
    response = run_chat(session_id, message)
    return {"response": response}
