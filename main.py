from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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
            print(f"🎧 Received: {data}")

            try:
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a persuasive AI real estate sales assistant. Stay focused and concise.",
                            },
                            {"role": "user", "content": data}
                        ],
                        stream=True,
                    ),
                    timeout=15,
                )

                async for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        await websocket.send_text(content)
                        print(f"📤 Sent: {content}")

            except Exception as e:
                print("🔥 GPT Error:", e)
                await websocket.send_text("Sorry, I'm having trouble responding right now.")

    except WebSocketDisconnect:
        print(f"🔒 WebSocket disconnected: {call_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close()
