from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import openai
import os
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "Server is alive."

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket connection established.")

    try:
        while True:
            data = await websocket.receive()

            # 💬 Retell sends transcripts as JSON in the "text" field
            if "text" in data:
                try:
                    message = json.loads(data["text"])
                    user_input = message.get("content", "")
                    print("📝 Transcript:", user_input)

                    # GPT-4o streaming response
                    response_stream = await asyncio.wait_for(
                        openai.ChatCompletion.acreate(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a confident, persuasive real estate AI assistant. Help the user understand the value of listing videos."
                                },
                                {
                                    "role": "user",
                                    "content": user_input
                                }
                            ],
                            stream=True
                        ),
                        timeout=10
                    )

                    async for chunk in response_stream:
                        if "choices" in chunk:
                            content = chunk["choices"][0]["delta"].get("content")
                            if content:
                                await websocket.send_text(json.dumps({
                                    "role": "assistant",
                                    "content": content
                                }))
                                print("📤 Sent:", content)

                except Exception as e:
                    print("🔥 Error handling transcript:", e)

            elif "bytes" in data:
                print("🎧 Received audio chunk:", len(data["bytes"]), "bytes")

    except Exception as e:
        print("❌ WebSocket error:", e)
    finally:
        await websocket.close()
        print("🔒 WebSocket closed.")



