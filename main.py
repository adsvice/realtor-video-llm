from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import openai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Root endpoint for Render
@app.get("/", response_class=PlainTextResponse)
async def root():
    return "✅ Render server is running."

# WebSocket endpoint for Retell
@app.websocket("/call_{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"🔌 WebSocket connected: {call_id}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"🎧 Received: {data}")

            # LLM response
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
                    ), timeout=15
                )

                async for chunk in response_stream:
                    if "choices" in chunk:
                        content = chunk["choices"][0].get("delta", {}).get("content")
                        if content:
                            await websocket.send_text(content)
                            print(f"📤 Sent: {content}")

            except Exception as e:
                print("🔥 GPT Error:", e)
                await websocket.send_text("Sorry, I'm having trouble right now.")

    except WebSocketDisconnect:
        print(f"🔒 WebSocket disconnected: {call_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close()

