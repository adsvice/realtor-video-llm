from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS middleware to avoid Retell browser simulator rejection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/", response_class=PlainTextResponse)
async def root():
    return "✅ Render server is running."

# WebSocket for Retell (with dynamic call ID path)
@app.websocket("/call_{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"🔌 WebSocket connected: {call_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"🎧 Received: {data}")

            try:
                response_stream = await asyncio.wait_for(
                    openai.ChatCompletion.acreate(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a persuasive AI real estate sales assistant. Stay focused and concise."
                            },
                            {
                                "role": "user",
                                "content": data
                            }
                        ],
                        stream=True
                    ),
                    timeout=15
                )

                async for chunk in response_stream:
                    if "choices" in chunk:
                        content = chunk["choices"][0].get("delta", {}).get("content")
                        if content:
                            await websocket.send_text(content)
                            print(f"📤 Sent: {content}")

            except Exception as e:
                error_trace = traceback.format_exc()
                print("🔥 GPT Exception Traceback:\n", error_trace)
                await websocket.send_text("⚠️ GPT failed:\n" + str(e))

    except WebSocketDisconnect:
        print(f"🔒 WebSocket disconnected: {call_id}")
    except Exception as e:
        print(f"❌ Unexpected WebSocket error: {e}")
        await websocket.close()
