import gradio as gr
import requests
import os
import time
from dotenv import load_dotenv

# Load env
load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

threads = {}
thread_count = 1
current_thread_name = f"chat{thread_count}"
threads[current_thread_name] = []

def chat_stream(message, history):
    global current_thread_name

    # Show user message
    history = history + [{"role": "user", "content": message}]
    threads[current_thread_name] = history
    yield history

    # Get bot response
    response = requests.post(API_URL, json={
        "session_id": current_thread_name,
        "message": message
    })

    if response.status_code != 200:
        bot_reply = f"Error: {response.text}"
    else:
        bot_reply = response.json()["response"]

    # Stream bot reply character-by-character
    partial = ""
    for char in bot_reply:
        time.sleep(0.02)
        partial += char
        history_display = history + [{"role": "assistant", "content": partial}]
        yield history_display

    # Save final bot message
    history = history + [{"role": "assistant", "content": bot_reply}]
    threads[current_thread_name] = history

def new_thread():
    global thread_count, current_thread_name
    thread_count += 1
    current_thread_name = f"chat{thread_count}"
    threads[current_thread_name] = []
    return gr.update(choices=list(threads.keys()), value=current_thread_name), []

def switch_thread(thread_name):
    global current_thread_name
    current_thread_name = thread_name
    return threads.get(thread_name, [])

with gr.Blocks() as demo:
    gr.Markdown("## Gemini LangGraph Chatbot with Streaming + Named Threads")

    thread_selector = gr.Dropdown(
        choices=[current_thread_name],
        value=current_thread_name,
        label="Select Thread"
    )
    new_thread_btn = gr.Button("➕ New Thread")

    chatbot = gr.Chatbot(type="messages", label="Chatbot")
    txt = gr.Textbox(placeholder="Type your message...", show_label=False)

    txt.submit(chat_stream, [txt, chatbot], chatbot)
    txt.submit(lambda: "", None, txt)

    new_thread_btn.click(
        new_thread, [], [thread_selector, chatbot]
    )

    thread_selector.change(
        switch_thread, [thread_selector], chatbot
    )

demo.launch()