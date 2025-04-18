from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import json

app = FastAPI()

# ✅ Required for Render to keep your app alive
@app.get("/")
async def root():
    return PlainTextResponse("Server is alive.")

# ✅ WebSocket endpoint for Retell
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive()

            # Handle transcript messages from Retell
            if "text" in data:
                try:
                    parsed = json.loads(data["text"])
                    user_input = parsed.get("content", "")
                    print("Transcript received:", user_input)

                    # 🔊 Hardcoded voice test response
                    await websocket.send_text(json.dumps({
                        "role": "assistant",
                        "content": "Hi there! This is your AI agent speaking. I'm live and ready."
                    }))

                except Exception as e:
                    print("Error parsing transcript:", e)

            # Handle audio chunks from Retell
            elif "bytes" in data:
                print("Audio chunk received:", len(data["bytes"]), "bytes")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        await websocket.close()







