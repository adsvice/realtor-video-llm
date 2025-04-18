from fastapi import FastAPI, WebSocket
import openai
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Server is alive."}

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive()

            if "text" in data:
                user_input = data["text"]
                print("Transcript:", user_input)

                try:
                    response_stream = await asyncio.wait_for(
                        openai.ChatCompletion.acreate(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a top-performing AI real estate sales assistant."},
                                {"role": "user", "content": user_input}
                            ],
                            stream=True
                        ),
                        timeout=10
                    )

                    async for chunk in response_stream:
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                await websocket.send_text(delta["content"])

                except Exception as e:
                    print("GPT-4o failed:", e)
                    await websocket.send_text("Sorry, I'm having trouble understanding you right now.")

            elif isinstance(data, bytes):
                print("Received audio chunk:", len(data), "bytes")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        await websocket.close()






