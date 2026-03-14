from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI()

# Разрешаем фронтенду обращаться к серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

CHAR_FILE = "characters.json"
if not os.path.exists(CHAR_FILE):
    with open(CHAR_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

with open(CHAR_FILE, "r", encoding="utf-8") as f:
    characters = json.load(f)

ADMIN_IDS = [6625239442, 7652697216]  # ТГ ID админов

# Модели данных
class Character(BaseModel):
    name: str
    desc: str
    img: str

class AddCharacter(BaseModel):
    adminId: int
    character: Character
    index: int = None

class ChatRequest(BaseModel):
    message: str
    charName: str
    userId: int
    userName: str

# Эндпоинты
@app.get("/api/characters")
def get_characters():
    return characters

@app.post("/api/characters")
def add_character(data: AddCharacter):
    if data.adminId not in ADMIN_IDS:
        return {"error": "Нет прав"}

    if data.index is not None and 0 <= data.index < len(characters):
        characters[data.index] = data.character.dict()
    else:
        characters.append(data.character.dict())

    with open(CHAR_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

    return {"success": True, "character": data.character.name}

# Чат-эндпоинт (GPT4Free)
@app.post("/api/chat")
def chat(req: ChatRequest):
    # Здесь подключаем GPT4Free
    # Для примера просто эхо-ответ
    char = next((c for c in characters if c['name'] == req.charName), None)
    if char:
        reply = f"{char['desc']}\n{req.userName}, {req.message} -> Ответ от {char['name']}"
    else:
        reply = f"Персонаж не найден."
    return {"reply": reply}
