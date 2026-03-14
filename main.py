# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json, os, asyncio, httpx

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- static ---
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- файлы данных ---
CHAR_FILE = "characters.json"
HISTORY_FILE = "history.json"

# --- загрузка персонажей ---
if os.path.exists(CHAR_FILE):
    with open(CHAR_FILE, "r", encoding="utf-8") as f:
        characters = json.load(f)
else:
    characters = []

# --- загрузка чатов ---
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        chat_history = json.load(f)
else:
    chat_history = {}

# --- глобальный httpx клиент для ускорения ---
client = httpx.AsyncClient(timeout=30.0)

# --- ROUTES ---

@app.get("/")
async def root():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "error", "msg": "index.html не найден в /static"})

# --- Персонажи ---
@app.get("/api/characters")
async def get_characters():
    return characters

@app.post("/api/characters")
async def add_character(request: Request):
    data = await request.json()
    character = data.get("character")
    if not character or "name" not in character or "desc" not in character:
        return JSONResponse({"status":"error","msg":"Некорректный персонаж"})
    characters.append(character)
    _save_characters()
    return {"status":"ok","characters":characters}

@app.put("/api/characters/{idx}")
async def update_character(idx: int, request: Request):
    data = await request.json()
    character = data.get("character")
    if not character or "name" not in character or "desc" not in character:
        return JSONResponse({"status":"error","msg":"Некорректный персонаж"})
    if 0 <= idx < len(characters):
        characters[idx] = character
        _save_characters()
        return {"status":"ok","characters":characters}
    return JSONResponse({"status":"error","msg":"Индекс вне диапазона"})

@app.delete("/api/characters/{idx}")
async def delete_character(idx: int):
    if 0 <= idx < len(characters):
        characters.pop(idx)
        _save_characters()
        return {"status":"ok","characters":characters}
    return JSONResponse({"status":"error","msg":"Персонаж не найден"})

# --- Чат с GPT4Free ---
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    msg = data.get("message", "")
    char_name = data.get("charName")
    msg = msg[:500]  # ограничение длины

    character = next((c for c in characters if c["name"]==char_name), None)
    if not msg or not character:
        return JSONResponse({"reply":"Сообщение пустое или персонаж не выбран."})

    prompt = f"Ты персонаж {character['name']}. {character['desc']}\nПользователь пишет: {msg}\nОтветь кратко и понятно:"

    # --- проверка и ускорение через один клиент ---
    try:
        response = await client.post(
            "https://gpt4free-api.vercel.app/api/generate",
            json={"prompt": prompt, "model": "gpt-4"}
        )
        resp_json = response.json()
        reply = resp_json.get("text") or "ИИ временно недоступен."
    except Exception as e:
        reply = f"Error communicating with GPT4Free: {str(e)}"

    # --- сохраняем чат ---
    key = f"{char_name}_{data.get('userId','guest')}"
    chat_history.setdefault(key, []).append({"t": msg, "s": "user"})
    chat_history[key].append({"t": reply, "s": "bot"})
    _save_history()

    return {"reply": reply}

# --- HELPERS ---
def _save_characters():
    with open(CHAR_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

def _save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

# --- Запуск сервера ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)