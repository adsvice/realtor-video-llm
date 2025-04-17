from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware  # 👈 Add this
import json

app = FastAPI()

# 👇 Add this CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        reply = {
            "role": "assistant",
            "content": "Hi, I'm your AI real estate sales assistant..."
        }
        await websocket.send_text(json.dumps(reply))
    except Exception as e:
        print("Error:", e)
    finally:
        await websocket.close()

