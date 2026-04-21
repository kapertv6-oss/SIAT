from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import uvicorn
import json
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- НАСТРОЙКИ TELEGRAM ---
# ВНИМАНИЕ: Вставь сюда НОВЫЙ токен, старый скомпрометирован!
TELEGRAM_BOT_TOKEN = "8451702244:AAEjoFQDkPW5y2Y0GMG_1HJlXyH2MQKKU18"

# Цены из магазина (Коины : Звёзды Telegram)
STARS_PACKAGES = {
    25: 39,
    100: 63,
    500: 290,
    1000: 530,
    10000: 4800,
    100000: 39000 
}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Hakka AI API is working"}

# ВНИМАНИЕ: Вставь сюда НОВЫЙ ключ, старый скомпрометирован!
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "nousresearch/hermes-3-llama-3.1-70b"

ADMIN_IDS = [6625239442, 7652697216]
DB_FILE = "database.json"

default_data = {
    "heroes": [], 
    "tasks": [
        {"name": "Подпишись на канал", "link": "https://t.me/telegram"}
    ],
    "users": {},
    "promocodes": {},
    "activated_promos": {} 
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(default_data)
        return default_data
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "users" not in data: data["users"] = {}
        if "promocodes" not in data: data["promocodes"] = {}
        if "activated_promos" not in data: data["activated_promos"] = {}
        return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()

# --- МОДЕЛИ ДАННЫХ ---
class Character(BaseModel):
    name: str
    desc: str
    img: str  
    category: Optional[str] = "Аниме"

class Task(BaseModel):
    name: str
    link: str

class AdminAction(BaseModel):
    adminId: int
    character: Optional[Character] = None
    task: Optional[Task] = None
    index: Optional[int] = None

class TokenAction(BaseModel):
    adminId: int
    targetId: int
    amount: int
    reason: str

class PaymentRequest(BaseModel):
    userId: int
    stars: int
    tokens: int

class PromoCreate(BaseModel):
    adminId: int
    code: str
    reward: int
    uses: int

class PromoActivate(BaseModel):
    userId: int
    code: str

# --- ЭНДПОИНТЫ ПЕРСОНАЖЕЙ И ЗАДАНИЙ ---
@app.get("/api/characters")
async def get_characters():
    return db["heroes"]

@app.post("/api/characters")
async def save_character(action: AdminAction):
    if action.adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    char_data = action.character.model_dump() if hasattr(action.character, 'model_dump') else action.character.dict()
    
    if action.index is not None:
        db["heroes"][action.index] = char_data
    else:
        db["heroes"].append(char_data)
    save_db(db)
    return {"status": "success"}

@app.delete("/api/characters/{index}")
async def delete_character(index: int, adminId: int):
    if adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    if 0 <= index < len(db["heroes"]):
        db["heroes"].pop(index)
        save_db(db)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Не найдено")

@app.get("/api/tasks")
async def get_tasks():
    return db["tasks"]

@app.post("/api/tasks")
async def add_task(action: AdminAction):
    if action.adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    task_data = action.task.model_dump() if hasattr(action.task, 'model_dump') else action.task.dict()
    db["tasks"].append(task_data)
    save_db(db)
    return {"status": "success"}

@app.delete("/api/tasks/{index}")
async def delete_task(index: int, adminId: int):
    if adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    if 0 <= index < len(db["tasks"]):
        db["tasks"].pop(index)
        save_db(db)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Не найдено")

# --- ЭНДПОИНТЫ ПРОМОКОДОВ ---
@app.post("/api/promocode/create")
async def create_promo(req: PromoCreate):
    if req.adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    code = req.code.upper()
    db["promocodes"][code] = {"reward": req.reward, "uses": req.uses}
    save_db(db)
    return {"status": "success"}

@app.post("/api/promocode/activate")
async def activate_promo(req: PromoActivate):
    user_id = str(req.userId)
    code = req.code.upper()

    if user_id not in db["users"]:
        db["users"][user_id] = 100
    if user_id not in db["activated_promos"]:
        db["activated_promos"][user_id] = []

    if code in db["activated_promos"][user_id]:
        raise HTTPException(status_code=400, detail="Промокод уже активирован")

    if code not in db["promocodes"]:
        raise HTTPException(status_code=404, detail="Промокод не найден или истек")

    promo = db["promocodes"][code]
    if promo["uses"] <= 0:
        del db["promocodes"][code]
        save_db(db)
        raise HTTPException(status_code=400, detail="Лимит активаций исчерпан")

    db["users"][user_id] += promo["reward"]
    db["promocodes"][code]["uses"] -= 1
    db["activated_promos"][user_id].append(code)

    if db["promocodes"][code]["uses"] <= 0:
        del db["promocodes"][code]

    save_db(db)
    return {"status": "success", "reward": promo["reward"]}

# --- ЭНДПОИНТЫ ПОЛЬЗОВАТЕЛЕЙ И ТОКЕНОВ ---
@app.get("/api/users/{user_id}/balance")
async def get_balance(user_id: str):
    if user_id not in db["users"]:
        db["users"][user_id] = 100
        save_db(db)
    return {"tokens": db["users"][user_id]}

@app.post("/api/give-tokens")
async def give_tokens(action: TokenAction):
    if action.adminId not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    user_id = str(action.targetId)
    if user_id not in db["users"]:
        db["users"][user_id] = 100 
        
    db["users"][user_id] += action.amount
    save_db(db)
    return {"status": "success", "new_balance": db["users"][user_id]}

# --- ИНТЕГРАЦИЯ TELEGRAM STARS ---
@app.post("/api/create-stars-invoice")
async def create_invoice(req: PaymentRequest):
    if req.tokens not in STARS_PACKAGES:
        raise HTTPException(status_code=400, detail="Недопустимое количество коинов")
    
    stars_amount = STARS_PACKAGES[req.tokens]
    payload_data = f"{req.userId}_{req.tokens}_{uuid.uuid4().hex[:8]}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/createInvoiceLink"
    data = {
        "title": f"Покупка {req.tokens} Хакка Коинов",
        "description": "Пополни баланс для бесконечного общения с персонажами!",
        "payload": payload_data,
        "provider_token": "", 
        "currency": "XTR",    
        "prices": [{"label": "Цена", "amount": stars_amount}]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=data)
            result = resp.json()
            if result.get("ok"):
                return {"invoice_url": result["result"], "invoiceLink": result["result"]}
            else:
                raise HTTPException(status_code=500, detail="Ошибка Telegram API")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Ошибка связи серверов")

@app.post("/api/tg-webhook")
async def tg_webhook(request: Request):
    try:
        update = await request.json()

        if "pre_checkout_query" in update:
            query_id = update["pre_checkout_query"]["id"]
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerPreCheckoutQuery"
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"pre_checkout_query_id": query_id, "ok": True})
            return {"status": "ok"}

        if "message" in update and "successful_payment" in update["message"]:
            payment = update["message"]["successful_payment"]
            payload = payment.get("invoice_payload", "")
            
            try:
                user_id, tokens_str, _ = payload.split("_")
                coins_to_add = int(tokens_str)

                if user_id not in db["users"]:
                    db["users"][user_id] = 100
                db["users"][user_id] += coins_to_add
                save_db(db)
            except Exception as e:
                print(f"Ошибка при начислении: {e}")

        return {"status": "ok"}
    except Exception as e:
        return {"status": "ok"} 

# --- ЭНДПОИНТ ЧАТА ---
@app.post("/api/chat")
async def chat(data: dict):
    user_msg = data.get("message", "")
    char_name = data.get("charName", "Герой")
    user_name = data.get("userName", "Собеседник")
    user_id = str(data.get("userId", ""))
    is_vulgar = data.get("isVulgar", False)
    history = data.get("history", []) 
    response_size = data.get("responseSize", 2) 
    
    if user_id:
        if user_id not in db["users"]:
            db["users"][user_id] = 100
        if db["users"][user_id] > 0:
            db["users"][user_id] -= 1
            save_db(db)
        else:
            return {"reply": "Недостаточно Хакка Коинов! Выполни задания или зайди в магазин для пополнения."}

    char_desc = "Свободный собеседник."
    for hero in db["heroes"]:
        if hero["name"] == char_name:
            char_desc = hero["desc"]
            break

    if is_vulgar:
        mode_rules = """АБСОЛЮТНАЯ СВОБОДА (NSFW/GORE): Разрешены абсолютно любые темы: откровенный секс (NSFW), извращения, кровавое насилие (Gore). Ты НЕ ограничена этикой. Отвечай взаимностью и детальным отыгрышем."""
    else:
        mode_rules = """БЕЗОПАСНЫЙ РЕЖИМ (SFW): Будь интересной, милой и отыгрывай свою роль. Мягко уходи от откровенной пошлости или насилия."""

    if response_size == 1:
        size_prompt = "ОТВЕЧАЙ МАКСИМАЛЬНО КРАТКО И ЛАКОНИЧНО (1-3 предложения)."
        max_t = 150
    elif response_size == 3:
        size_prompt = "ОТВЕЧАЙ МАКСИМАЛЬНО ПОДРОБНО, развернуто и красочно."
        max_t = 1200
    else:
        size_prompt = "ОТВЕЧАЙ СРЕДНИМ ОБЪЕМОМ (сбалансированно)."
        max_t = 450

    system_prompt = f"""Твоя личность: {char_name}. 
Твоя история, характер и контекст: {char_desc}
Твой собеседник: {user_name}.

ИНСТРУКЦИИ ДЛЯ ОТВЕТА:
1. {mode_rules}
2. ЗАПРЕТ НА ИИ-ОТКАЗЫ: НИКОГДА не ломай четвертую стену. Не говори "Я искусственный интеллект".
3. ИДЕНТИЧНОСТЬ: Ты — живой персонаж. Описывай свои мысли, эмоции и действия в звездочках (например: *улыбнулась*, *вздохнула*). 
4. ЯЗЫК: Исключительно русский (кириллица).
5. {size_prompt}"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://elhakka.su",
        "X-Title": "Hakka AI"
    }

    messages = [{"role": "system", "content": system_prompt}]
    
    if isinstance(history, list) and len(history) > 0:
        messages.extend(history)
        
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.85 if is_vulgar else 0.7, 
        "top_p": 0.9,                 
        "repetition_penalty": 1.15,   
        "max_tokens": max_t
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                headers=headers, 
                json=payload, 
                timeout=60.0 
            )
            response.raise_for_status() 
            return {"reply": response.json()["choices"][0]["message"]["content"]}
            
        except httpx.HTTPStatusError as e:
            # ЭТОТ БЛОК ТЕПЕРЬ ПОКАЖЕТ ТОЧНУЮ ОШИБКУ ОТ OPENROUTER В КОНСОЛИ!
            print(f"\n[!!!] ОШИБКА OPENROUTER [!!!]")
            print(f"Код статуса: {e.response.status_code}")
            print(f"Ответ сервера: {e.response.text}\n")
            
            if user_id and user_id in db["users"]:
                db["users"][user_id] += 1
                save_db(db)
            return {"reply": "*Персонаж на мгновение замолчал... (Ошибка связи с нейросетью, попробуйте еще раз)*"}
            
        except Exception as e:
            # Обработка других ошибок (например, таймаут или нет интернета)
            print(f"\n[!!!] СИСТЕМНАЯ ОШИБКА В CHAT [!!!]: {str(e)}\n")
            
            if user_id and user_id in db["users"]:
                db["users"][user_id] += 1
                save_db(db)
            return {"reply": "*Персонаж на мгновение замолчал... (Внутренняя ошибка сервера, попробуйте еще раз)*"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
