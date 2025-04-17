import os, json, asyncio, tiktoken
from fastapi import FastAPI, WebSocket
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup tokenizer + OpenAI client
ENC = tiktoken.encoding_for_model("gpt-4o-mini")
client = AsyncOpenAI()

# Set the system prompt — TEMP TEST
SYSTEM_PROMPT = "🚨 TEST MODE: THIS IS NOT A THERAPIST. THIS IS KAI, AI SALES AGENT."

print("🔥 SYSTEM PROMPT LOADED:", SYSTEM_PROMPT)

app = FastAPI()

@app.websocket("/ws/challenger-spin")
async def llm(ws: WebSocket):
    await ws.accept()
    print("💬 WebSocket connection accepted")
    
    await ws.send_text(json.dumps({
        "interaction_type": "config",
        "auto_reconnect": True
    }))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        incoming = json.loads(await ws.receive_text())

        if incoming["interaction_type"] == "ping_pong":
            await ws.send_text(json.dumps({"interaction_type": "pong"}))
            continue
        if incoming["interaction_type"] != "response_required":
            continue

        print("📩 Incoming user message:", incoming["user_text"])
        messages.append({"role": "user", "content": incoming["user_text"]})

        # Trim history to fit token limit
        while sum(len(ENC.encode(m["content"])) for m in messages) > 8000:
            messages.pop(1)

        # Call OpenAI
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=256,
            stream=False
        )

        answer = resp.choices[0].message.content
        print("🤖 Kai response:", answer)

        messages.append({"role": "assistant", "content": answer})
        await ws.send_text(json.dumps({
            "interaction_type": "response",
            "content": answer
        }))

