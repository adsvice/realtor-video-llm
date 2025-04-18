from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import json
import openai
import asyncio
import os

app = FastAPI()

# ✅ Keep Render alive
@app.get("/")
async def root():
    return PlainTextResponse("Server is alive.")

# 🔐 OpenAI key from environment or hardcoded
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...REPLACE_ME...")

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive()

            if "text" in data:
                try:
                    parsed = json.loads(data["text"])
                    user_input = parsed.get("content", "")
                    print("Transcript received:", user_input)

                    # 🔥 Stream GPT-4o response
                    response_stream = await asyncio.wait_for(
                        openai.ChatCompletion.acreate(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a persuasive real estate AI voice agent. Speak clearly, confidently, and ask questions to qualify leads."},
                                {"role": "user", "content": user_input}
                            ],
                            stream=True
                        ),
                        timeout=10
                    )

                    async for chunk in response_stream:
                        if "choices" in chunk:
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                await websocket.send_text(json.dumps({
                                    "role": "assistant",
                                    "content": delta["content"]
                                }))

                except asyncio.TimeoutError:
                    print("⏳ GPT-4o timed out")
                    await websocket.send_text(json.dumps({
                        "role": "assistant",
                        "content": "Sorry, I didn’t catch that. Could you say it again?"
                    }))
                except Exception as e:
                    print("❌ GPT-4o error:", e)

            elif "bytes" in data:
                print("Audio chunk received:", len(data["bytes"]), "bytes")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        await websocket.close()






