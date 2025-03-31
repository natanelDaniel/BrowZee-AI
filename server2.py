from browser_use.agent import service
from fastapi import FastAPI, WebSocket
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import os
from langchain_openai import ChatOpenAI
from browser_use import Agent
from browser_use import BrowserConfig
from browser_use import Browser
from typing import Optional
from typing_extensions import Annotated, TypedDict
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from browser_use.agent.service import wait_for_user_response, receive_user_response
from browser_use.agent.service import websocket_endpoint, app  # ייבוא מהשירות
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from browser_use.agent.service import send_to_websockets

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # אפשר הכל כדי לבדוק
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
active_agent = None

class TaskRequest(BaseModel):
    task: str
    mode: Literal["task", "chat", "chat-this-page"]


class StatusRequest(BaseModel):
    status: str
    question: Optional[str] = None


class NeedAgent(TypedDict):
    is_need_agent: Annotated[bool, 'the task need an agent to complete']
    answer: Annotated[Optional[str], 'the answer of the model - to the question of the user - without mentioning the agent and if there is a need for an agent, for example - the user ask 1+1 and the model answer 2']


@app.get("/")
def root():
    return {"status": "ok"}

@app.websocket("/ws/status")
async def websocket_status(websocket):
    await websocket_endpoint(websocket)

@app.post("/stop-task")
async def stop_task():
    global active_agent  # ← THIS IS IMPORTANT
    if active_agent is not None:
        active_agent.stop()
        await send_to_websockets("🛑 Task stopped by user.")
        active_agent = None
        return {"status": "stopped"}
    return {"status": "no_active_task"}

@app.post("pause-task")
async def pause_task():
    global active_agent
    if active_agent is not None:
        active_agent.pause()
        active_agent.state.paused = True
        await send_to_websockets("⏸ Task paused by user.")
        return {"status": "paused"}
    return {"status": "no_active_task"}

@app.post("resume-task")
async def resume_task():
    global active_agent
    if active_agent is not None:
        active_agent.resume()
        active_agent.state.paused = False
        await send_to_websockets("▶ Task resumed by user.")
        return {"status": "resumed"}
    return {"status": "no_active_task"}

@app.post("/run-task")
async def run_task(request: TaskRequest):
    global active_agent

    task_text = request.task
    mode = request.mode
    print(f"Received {mode}: {task_text}")

    if request.mode == "chat-this-page":
        from io import BytesIO
        import base64
        import pygetwindow as gw
        import pyautogui

        def image_to_base64(pil_image) -> str:
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{img_str}"

        windows = gw.getWindowsWithTitle("Chromium")
        if windows:
            browser_window = windows[0]
            left, top, width, height = browser_window.left, browser_window.top, browser_window.width, browser_window.height
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot_base64 = image_to_base64(screenshot)

            message_text = f"""This is a screenshot of the current web page. The user asked:\n"{task_text}"\nAnswer based on the visual content if possible."""
            messages = [HumanMessage(content=[
                {"type": "text", "text": message_text},
                {"type": "image_url", "image_url": {"url": screenshot_base64}}
            ])]
            answer = await model.ainvoke(messages)
            await send_to_websockets(answer.content)
            return answer
        else:
            error_msg = "❌ No Chromium window found for screenshot."
            await send_to_websockets(error_msg)
            return {"error": error_msg}
    elif mode == "chat":
        answer = await model.ainvoke([HumanMessage(content=task_text)])
        await send_to_websockets(answer.content)
        return answer

    elif mode == "task" or mode == "interactive-task":
        global active_agent
        if active_agent is not None:
            return
        user_path = os.environ["USERPROFILE"]
        chrome_path = os.path.join(user_path, "AppData", "Local", "Chromium", "Application", "chrome.exe")

        config = BrowserConfig(chrome_instance_path=chrome_path)
        browser = Browser(config=config)

        if mode == "interactive-task":
            interactive = True
        else:
            interactive = False
        active_agent = Agent(
            browser=browser,
            task=task_text,
            llm=ChatOpenAI(model="gpt-4o"),
            send_to_websockets_flag=True, interactive=interactive
        )
        agent_result = await active_agent.run_interactive()
        result = agent_result.final_result()
        active_agent = None
        await send_to_websockets(result)
        return result


# הרצה (אם תרצה)
# uvicorn ai_server:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    load_dotenv()

    # Manually set the API key if needed
    os.environ[
        "OPENAI_API_KEY"] = "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"
    need_agent_model = ChatOpenAI(model="gpt-4o").with_structured_output(NeedAgent, include_raw=True)
    model = ChatOpenAI(model="gpt-4o-mini")
    uvicorn.run(app, host="127.0.0.1", port=8000,log_config=None)