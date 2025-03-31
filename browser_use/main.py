import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import os
from langchain_openai import ChatOpenAI
from .agent.service import Agent
from .browser import BrowserConfig
from .browser import Browser
from typing import Optional
import asyncio

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

class StatusRequest(BaseModel):
    status: str
    question: Optional[str] = None

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/run-task")
async def run_task(request: TaskRequest):
    task_text = request.task
    print(f"Received task: {task_text}")
    user_path = os.environ["USERPROFILE"]
    chrome_path = os.path.join(user_path, "AppData", "Local", "Chromium", "Application", "chrome.exe")

    config = BrowserConfig(
        chrome_instance_path=chrome_path
    )
    browser = Browser(config=config)
    # הרצת הסוכן
    agent = Agent(
        browser=browser,
        task=task_text,
        llm=ChatOpenAI(model="gpt-4o")
    )
    agent_result = await agent.run_interactive()

    return agent_result.final_result()

@app.post("/agent-status")
async def agent_status(request: StatusRequest):
    status_text = request.status
    question_text = request.question
    print(f"Agent Status: {status_text}")
    if question_text:
        print(f"Agent Question: {question_text}")
        # כאן נוכל להוסיף לוגיקה להמתין לתשובת המשתמש
    return {"status": "received", "question": question_text}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # כאן נוכל להוסיף לוגיקה לשליחת עדכונים
            await websocket.send_text("Waiting for updates...")
            await asyncio.sleep(1)  # זמן המתנה לדוגמה
    except Exception as e:
        print(f"WebSocket error: {e}")

# הרצה (אם תרצה)
# uvicorn ai_server:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    load_dotenv()

    # Manually set the API key if needed
    os.environ[
        "OPENAI_API_KEY"] = "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"

    uvicorn.run(app, host="127.0.0.1", port=8000,log_config=None) 