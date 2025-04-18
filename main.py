from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import openai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Health check endpoint for Render
@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Server is alive."

# WebSocket endpoint for Retell
@app.websocket("/call_{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"📞 Connected to call ID: {call_id}")

    try:
        async for data in websocket.iter_bytes():
            print("🎧 Received audio chunk:", len(data), "bytes")

            # You can stream audio to Whisper here, if needed
            # Placeholder transcript for testing
            user_text = "Tell me about your real estate video service."

            try:
                response_stream = await asyncio.wait_for(
                    openai.ChatCompletion.acreate(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a top-performing AI real estate sales assistant. Speak clearly and concisely."
                            },
                            {
                                "role": "user",
                                "content": user_text
                            }
                        ],
                        stream=True
                    ), timeout=10
                )

                async for chunk in response_stream:
                    if "choices" in chunk:
                        content = chunk["choices"][0].get("delta", {}).get("content")
                        if content:
                            await websocket.send_text(content)
                            print("📤 Sent:", content)

            except Exception as e:
                print("🔥 GPT-4o failed:", e)
                await websocket.send_text("Sorry, I'm having trouble responding right now.")

    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        await websocket.close()
        print("🔒 WebSocket connection closed.")
