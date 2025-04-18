from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import openai
import os
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
            data = await websocket.receive_text()
            print(f"🎧 Received from Retell: {data}")

            try:
                # OpenAI GPT streaming response
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
                print("🔥 GPT-4o ERROR:", e)
                traceback.print_exc()
                await websocket.send_text("Sorry, I'm having trouble responding right now.")

    except WebSocketDisconnect:
        print(f"🔒 WebSocket disconnected: {call_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        traceback.print_exc()
        await websocket.close()

