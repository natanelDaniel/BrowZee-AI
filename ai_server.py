from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
import os
# ייבוא ה-Agent וה-LLM שלך
from langchain_openai import ChatOpenAI
from browser_use import Agent
from fastapi.responses import HTMLResponse

app = FastAPI()

class TaskRequest(BaseModel):
    task: str


@app.post("/run-task")
async def run_task(request: TaskRequest):
    task_text = request.task
    print(f"Received task: {task_text}")

    # הרצת הסוכן
    agent = Agent(
        task=task_text,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    agent_result = await agent.run()

    return agent_result.final_result()
# הרצה (אם תרצה)
# uvicorn ai_server:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    import os

    load_dotenv()

    # Manually set the API key if needed
    os.environ[
        "OPENAI_API_KEY"] = "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"

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
