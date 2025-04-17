from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# HTTP CORS (for regular API calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)

# WebSocket CORS (critical for Retell)
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    # Explicitly allow all origins for WebSocket
    await websocket.accept()
    
    try:
        data = await websocket.receive_text()
        print("Received:", data)  # Check Render logs
        
        await websocket.send_text(json.dumps({
            "role": "assistant",
            "content": "Hi, I'm your AI real estate sales assistant..."
        }))
        
    except Exception as e:
        print("WS Error:", e)
    finally:
        await websocket.close()