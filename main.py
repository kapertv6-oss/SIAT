from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json, os, httpx

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files ---
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Data files ---
CHAR_FILE = "characters.json"
HISTORY_FILE = "history.json"

# --- Admins ---
ADMIN_IDS = [6625239442, 7652697216]  # добавь свои ID

# --- Load characters ---
if os.path.exists(CHAR_FILE):
    with open(CHAR_FILE, "r", encoding="utf-8") as f:
        characters = json.load(f)
else:
    characters = []

# --- Load chat history ---
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        chat_history = json.load(f)
else:
    chat_history = {}

# --- ROUTES ---
@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/api/characters")
async def get_characters():
    return characters

@app.post("/api/characters")
async def add_character(request: Request):
    data = await request.json()
    admin_id = data.get("adminId")
    character = data.get("character")
    if admin_id not in ADMIN_IDS:
        return JSONResponse({"status":"error","msg":"Вы не админ"})
    if not character or "name" not in character or "desc" not in character or "img" not in character:
        return JSONResponse({"status":"error","msg":"Некорректный персонаж"})
    idx = data.get("index")
    if idx is not None and 0 <= idx < len(characters):
        characters[idx] = character
    else:
        characters.append(character)
    _save_characters()
    return JSONResponse({"status":"ok","characters":characters,"msg":"Персонаж успешно добавлен"})

@app.delete("/api/characters/{idx}")
async def delete_character(idx: int, adminId: int = 0):
    if adminId not in ADMIN_IDS:
        return JSONResponse({"status":"error","msg":"Вы не админ"})
    if 0 <= idx < len(characters):
        characters.pop(idx)
        _save_characters()
        return {"status":"ok","characters":characters}
    return JSONResponse({"status":"error","msg":"Персонаж не найден"})

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    msg = data.get("message")
    char_name = data.get("charName")
    character = next((c for c in characters if c["name"]==char_name), None)
    if not msg or not character:
        return JSONResponse({"reply":"Сообщение пустое или персонаж не выбран."})

    # История для ИИ
    key = f"{char_name}_{data.get('userId','guest')}"
    history = chat_history.get(key, [])
    history_text = "\n".join([f"Пользователь: {m['t']}" if m['s']=='user' else f"{char_name}: {m['t']}" for m in history[-10:]])

    # Скрытый промпт для ИИ
    prompt = f"""
Ты персонаж {character['name']}.
{character['desc']}
Никогда не признавай, что ты ИИ. Используй *действия*, внутренние мысли, эмоции.
Отвечай развернуто, можешь развивать роман, драму, конфликт или любые сцены.
История диалога:
{history_text}

Пользователь пишет: {msg}
Отвечай как настоящий персонаж, используя *действия*, эмоции, внутренние мысли. Никогда не признавай, что ты ИИ.
"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://gpt4free-api.vercel.app/api/generate",
                json={"prompt": prompt, "model": "gpt-4", "temperature":0.9, "max_tokens":600}
            )
            resp_json = response.json()
            reply = resp_json.get("text", "ИИ временно недоступен.")
    except Exception as e:
        reply = f"Ошибка связи с ИИ: {str(e)}"

    # Сохраняем историю
    history.append({"t": msg, "s": "user"})
    history.append({"t": reply, "s": "bot"})
    chat_history[key] = history[-50:]  # храним последние 50 сообщений
    _save_history()

    return {"reply": reply}

# --- HELPERS ---
def _save_characters():
    with open(CHAR_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

def _save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
