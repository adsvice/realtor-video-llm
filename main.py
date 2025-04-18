from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "✅ Render server is running."

@app.websocket("/call_{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"🔌 WebSocket connected: {call_id}")

    try:
        while True:
            user_input = await websocket.receive_text()
            print(f"🎧 Received: {user_input}")

            try:
                response_stream = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a persuasive AI real estate sales assistant. Stay focused and concise."
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    stream=True
                )

                async for chunk in response_stream:
                    if chunk.choices:
                        content = chunk.choices[0].delta.content
                        if content:
                            await websocket.send_text(content)
                            print(f"📤 Sent: {content}")

            except Exception as e:
                print("🔥 GPT Error:", e)
                await websocket.send_text(f"⚠️ GPT failed: {type(e).__name__} - {e}")

    except WebSocketDisconnect:
        print(f"🔒 WebSocket disconnected: {call_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close()

