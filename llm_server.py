from fastapi import FastAPI, WebSocket
import json

app = FastAPI()

@app.get("/")  # 👈 Add this to keep Render happy
def root():
    return {"status": "WebSocket server is up"}

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    data = await websocket.receive_text()
    parsed = json.loads(data)

    reply = {
        "role": "assistant",
        "content": "Hi, I'm your AI real estate sales assistant. How can I help you today?"
    }

    await websocket.send_text(json.dumps(reply))
    await websocket.close()


