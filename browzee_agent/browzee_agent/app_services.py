from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from asyncio import Future
from typing import Optional
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # אפשר הכל כדי לבדוק
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# שמור את החיבורים של ה-WebSocket
websockets = []

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    global websocket_connection
    await websocket.accept()
    websocket_connection = websocket
    websockets.append(websocket)  # ← הוספת החיבור לרשימה
    try:
        while True:
            data = await websocket.receive_text()
            await receive_user_response(data)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_connection = None
        websockets.remove(websocket)  # ← הסרת החיבור לאחר ניתוק

user_response_future: Future = None

websocket_connection: Optional[WebSocket] = None

async def wait_for_user_response(question: str) -> str:
	global user_response_future, websocket_connection
	user_response_future = Future()

	if websocket_connection:
		await websocket_connection.send_text(question)
	else:
		raise Exception("No active WebSocket connection to user")

	return await user_response_future

async def send_to_websockets(message: str):
    for ws in websockets:
        await ws.send_text(message)


async def receive_user_response(answer: str):
	global user_response_future
	if user_response_future and not user_response_future.done():
		user_response_future.set_result(answer)
