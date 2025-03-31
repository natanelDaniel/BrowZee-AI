from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

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


async def send_to_websockets(message: str):
    for ws in websockets:
        await ws.send_text(message)