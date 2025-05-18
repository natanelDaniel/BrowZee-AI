from browzee_agent.agent import service
from fastapi import FastAPI, WebSocket
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import os
from langchain_openai import ChatOpenAI
from browzee_agent import Agent
from browzee_agent import BrowserConfig
from browzee_agent import Browser
from fastapi.responses import FileResponse
from typing import Optional
from typing_extensions import Annotated, TypedDict
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
import subprocess, pathlib, asyncio, httpx
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import aiohttp
from langchain_xai import ChatXAI
from langchain_google_genai import ChatGoogleGenerativeAI
import sys
import winreg
from fastapi.responses import FileResponse
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
from browzee_agent.app_services import app, send_to_websockets, websocket_endpoint
from langchain_mcp import MCPToolkit
import requests
from pathlib import Path
import pathlib
# GMAIL_MCP_PATH = pathlib.Path(__file__).parent / "deps" / "gmail_mcp"
# sys.path.append(str(GMAIL_MCP_PATH))
# BASE_DIR = Path(__file__).resolve().parent          # תיקיית server2.py
# COMPOSE_DIR = BASE_DIR / "opt" / "gmail-mcp"        # opt\gmail-mcp תחת הפרויקט
# COMPOSE_FILE = COMPOSE_DIR / "docker-compose.yml"

active_agent = None
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
class TaskRequest(BaseModel):
    task: str
    mode: Literal["task", "chat", "chat-this-page", "interactive-task"]


class StatusRequest(BaseModel):
    status: str
    question: Optional[str] = None


class SearchRequest(BaseModel):
    query: str


class NeedAgent(TypedDict):
    is_need_agent: Annotated[bool, 'the task need an agent to complete']
    answer: Annotated[Optional[str], 'the answer of the model - to the question of the user - without mentioning the agent and if there is a need for an agent, for example - the user ask 1+1 and the model answer 2']

@app.get("/status")
async def status():
    """Simple endpoint to check if the server is running"""
    return {"status": "ok", "server": "BrowZee Agent", "version": "1.0"}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_browzee_path():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Browzee", 0, winreg.KEY_READ)
        install_dir, _ = winreg.QueryValueEx(registry_key, "Install_Dir")
        winreg.CloseKey(registry_key)
        return os.path.join(install_dir, "browzee.exe")
    except Exception as e:
        print(f"Error locating Browzee: {e}")
        return None

 # server2.py   (קטעים רלוונטיים)
# from server.main import create_app as create_gmail_mcp
# from hypercorn.asyncio import serve
# from hypercorn.config import Config
# import asyncio, pathlib

# MCP_PORT = 5080
# MCP_URL  = f"http://localhost:{MCP_PORT}"
# MCP_DIR  = pathlib.Path(__file__).parent / "opt" / "gmail-mcp"

# @app.on_event("startup")
# async def startup():
#     gmail_app = create_gmail_mcp(
#         oauth_path="deps/gmail_mcp/client_secret.json",     # או נתיב אחר
#         credentials_dir="deps/gmail_mcp/credentials"
#     )
#     cfg = Config()
#     cfg.bind = ["localhost:5080"]
#     asyncio.create_task(serve(gmail_app, cfg))

#     # 2. ממתין שה‑/manifest יהיה זמין (polling קצר)
#     import httpx, time
#     async with httpx.AsyncClient() as c:
#         for _ in range(30):            # עד 3 שניות
#             try:
#                 r = await c.get(f"{MCP_URL}/manifest")
#                 if r.status_code == 200:
#                     break
#             except httpx.TransportError:
#                 pass
#             await asyncio.sleep(0.1)
#         else:
#             raise RuntimeError("Gmail‑MCP did not start")

#     # 3. טוען את הכלים
#     from langchain_mcp_adapters.client import MultiServerMCPClient
#     client = MultiServerMCPClient({"gmail": MCP_URL})
#     tools  = await client.load_tools_async()

#     from langchain_openai import ChatOpenAI
#     from langgraph.prebuilt import create_react_agent
#     app.state.agent = create_react_agent(llm=ChatOpenAI(model="gpt-4.1"), tools=tools)
   

@app.get("/page")
def root():
    html_path = resource_path("main_gui.html")
    return FileResponse(html_path)

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

        windows = gw.getWindowsWithTitle("Browzee")
        if windows:
            browser_window = windows[0]
            left, top, width, height = browser_window.left, browser_window.top, browser_window.width, browser_window.height
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot_base64 = image_to_base64(screenshot)
            messages = [
                HumanMessage(content=[
                    {"type": "text",
                     "text": f'This is a screenshot of the current web page. The user asked:\n"{task_text}"\nAnswer based on the visual content if possible.'},
                    {"type": "image_url", "image_url": {"url": screenshot_base64}}
                ])
            ]
            answer = await vision_model.ainvoke(messages)
            await send_to_websockets(answer.content)
            # Update memory with both text + response
            # active_agent.memory.message_manager.state.history.messages += [HumanMessage(content=f"User was asked: {task_text}\nUser answered: {answer.content}")]

            return answer
        else:
            error_msg = "❌ No Chromium window found for screenshot."
            await send_to_websockets(error_msg)
            return {"error": error_msg}
    elif mode == "chat":
        # subprocess.run(
        #     ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"],
        #     cwd=str(COMPOSE_DIR),            #  <‑‑ מפעיל מתוך אותה תיקייה
        #     check=True
        # )
        # # 2. httpx client אחד לכל החיים
        # app.state.httpx = httpx.AsyncClient(timeout=30.0)

        messages = [
            HumanMessage(content=task_text)
        ]
        answer = await model.ainvoke(messages)
        # answer = await model.ainvoke([HumanMessage(content=task_text)])
        # app.state.mcp = MultiServerMCPClient(
        #     {"gmail": {"url": "http://localhost:8080"}},  # אין צורך headers
        #     session=app.state.httpx
        # )
        # app.state.mcp_tools = await app.state.mcp.load_tools_async()

        # app.state.agent = create_react_agent(
        #     model=model,
        #     tools=app.state.mcp_tools,
        #     verbose=True
        # )
        await send_to_websockets(answer["messages"][-1].content)
        return answer

    elif mode == "task" or mode == "interactive-task":
        if active_agent is not None:
            return
        if mode == "interactive-task":
            interactive = True
        else:
            interactive = False
        planner_llm = model
        active_agent = Agent(
            browser=browser,
            task=task_text,
            enable_memory=True,
            llm=model,
            send_to_websockets_flag=True, interactive=interactive, planner_llm=planner_llm, vision_model=vision_model
        )
        agent_result = await active_agent.run_interactive()
        result = agent_result.final_result()
        active_agent = None
        if type(request) is not None:
            result = "Task completed.\n" + result
        else:
            result = "Task stopped.\n"
        await send_to_websockets(result)
        return result

@app.post("/search-proxy")
async def search_proxy(request: SearchRequest):
    """Handle search queries from the Ask functionality"""
    try:
        print(f"Processing search query: {request.query}")
        # Use the Claude model to answer the query
        messages = [
            SystemMessage(content="""You are BrowZee AI Assistant, a helpful and intelligent assistant. 
            Provide clear, direct answers to questions. When appropriate, include suggestions for follow-up tasks that the user might want to perform.
            Format your answers in clean, readable text without unnecessary markdown."""),
            HumanMessage(content=request.query)
        ]
        
        response = await model.ainvoke(messages)
        answer_text = response.content
        
        # Extract potential tasks from the answer
        tasks = None
        if "you might want to" in answer_text.lower() or "you could" in answer_text.lower() or "consider" in answer_text.lower():
            # Simple attempt to extract suggested tasks
            try:
                # Look for task suggestions at the end of the response
                tasks_content = None
                if "tasks you might consider:" in answer_text.lower():
                    tasks_content = answer_text.split("tasks you might consider:", 1)[1].strip()
                elif "suggested tasks:" in answer_text.lower():
                    tasks_content = answer_text.split("suggested tasks:", 1)[1].strip()
                elif "suggestions:" in answer_text.lower():
                    tasks_content = answer_text.split("suggestions:", 1)[1].strip()
                
                if tasks_content:
                    tasks = tasks_content
                    # Remove the tasks section from the main answer
                    answer_text = answer_text.replace(tasks_content, "").replace("Tasks you might consider:", "").replace("Suggested tasks:", "").replace("Suggestions:", "").strip()
            except Exception as e:
                print(f"Error extracting tasks: {e}")
        
        return {"answer": answer_text, "tasks": tasks}
    except Exception as e:
        print(f"Error in search proxy: {e}")
        return {"error": str(e)}, 500

# הרצה (אם תרצה)
# uvicorn ai_server:app --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv()

    # Manually set the API key if needed
    # os.environ["OPENAI_API_KEY"] = "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"
    os.environ["OPENAI_API_KEY"] = "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"
    os.environ["GROK_API_KEY"] = "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"
    os.environ["XAI_API_KEY"] = "xai-CXLn9LJRVLjaQvAhHEvIQeaQ6xlRZkdYVUUrBLCxhNWBlHUhNRe4VOs2GXUFdMLIsPPZrFnUzMnnzLHe"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDgn2-ifVfkIM9Fye9JFa-jNF7CxtyE9V8"
    # "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"
    # model = ChatOpenAI(model="gpt-4o")
    model = ChatOpenAI(model="gpt-4.1")
    vision_model_name = "gemini-2.0-flash"
    vision_model = ChatGoogleGenerativeAI(model=vision_model_name)

    from browzee_agent.browser.context import BrowserContextConfig
    browzee_path = get_browzee_path()
    context_config = BrowserContextConfig(
        permissions=["geolocation", "notifications", "camera", "microphone", "clipboard-read", "clipboard-write"]
    )
    config = BrowserConfig(chrome_instance_path=browzee_path, headless=False, new_context_config=context_config)
    browser = Browser(config=config)

    uvicorn.run(app, host="127.0.0.1", port=8000,log_config=None)