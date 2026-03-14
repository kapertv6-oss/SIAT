from fastapi import FastAPI
from pydantic import BaseModel
import json, asyncio
from gpt4free import Provider, ChatCompletion  # пример gpt4free

app = FastAPI()
CHAR_FILE = "characters.json"

with open(CHAR_FILE, "r", encoding="utf-8") as f:
    characters = json.load(f)

class ChatMessage(BaseModel):
    userId: int
    charName: str
    userName: str
    message: str

# Используем GPT4Free
provider = Provider.ABC  # заменить на реальный провайдер из gpt4free

@app.post("/api/chat")
async def chat(msg: ChatMessage):
    char = next((c for c in characters if c["name"] == msg.charName), None)
    if not char: return {"reply": "Персонаж не найден!"}

    prompt = (
        f"Ты — {char['name']}.\n"
        f"Описание: {char['desc']}\n"
        f"Не упоминай, что ты ИИ.\n"
        f"Используй действия и эмоции.\n"
        f"Сообщение пользователя: {msg.message}\n"
        f"Ответь как персонаж, коротко и быстро."
    )

    # Асинхронный быстрый вызов GPT4Free
    try:
        reply = await ChatCompletion.create(
            provider=provider,
            prompt=prompt,
            max_tokens=150,   # меньше токенов = быстрее ответ
            stream=False      # если True — можно стримить сразу
        )
    except Exception:
        reply = "Ошибка AI"

    return {"reply": reply}
