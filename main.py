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

# Настройки реферальной системы (Коины)
REF_REWARD_REFERRER = 50  # Сколько получает тот, кто пригласил
REF_REWARD_NEW_USER = 25  # Сколько получает тот, кто перешел по ссылке

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
    "activated_promos": {},
    "referrals_claimed": {}, # {"new_user_id": "referrer_id"}
    "referrals_stats": {}    # {"user_id": count_of_invites}
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
        if "referrals_claimed" not in data: data["referrals_claimed"] = {}
        if "referrals_stats" not in data: data["referrals_stats"] = {}
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

class ReferralActivate(BaseModel):
    userId: int
    referrerId: int

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

# --- ЭНДПОИНТЫ РЕФЕРАЛЬНОЙ СИСТЕМЫ ---
@app.post("/api/referral/activate")
async def activate_referral(req: ReferralActivate):
    user_id = str(req.userId)
    referrer_id = str(req.referrerId)

    if user_id == referrer_id:
        raise HTTPException(status_code=400, detail="Нельзя пригласить самого себя")

    if user_id in db["referrals_claimed"]:
        raise HTTPException(status_code=400, detail="Вы уже активировали реферальную ссылку")

    # Инициализируем юзеров, если их еще нет в базе
    if user_id not in db["users"]:
        db["users"][user_id] = 100
    if referrer_id not in db["users"]:
        db["users"][referrer_id] = 100

    # Начисляем награды
    db["users"][user_id] += REF_REWARD_NEW_USER
    db["users"][referrer_id] += REF_REWARD_REFERRER

    # Записываем, что юзер использовал рефералку и плюсуем стату рефоводу
    db["referrals_claimed"][user_id] = referrer_id
    db["referrals_stats"][referrer_id] = db["referrals_stats"].get(referrer_id, 0) + 1

    save_db(db)
    
    return {
        "status": "success", 
        "message": "Реферальная ссылка успешно активирована",
        "reward_user": REF_REWARD_NEW_USER,
        "reward_referrer": REF_REWARD_REFERRER
    }

@app.get("/api/users/{user_id}/referral-stats")
async def get_referral_stats(user_id: str):
    # Возвращает статистику по приглашенным
    count = db["referrals_stats"].get(user_id, 0)
    return {
        "invites_count": count,
        "total_earned": count * REF_REWARD_REFERRER
    }

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
            print(f"\n[!!!] ОШИБКА OPENROUTER [!!!]")
            print(f"Код статуса: {e.response.status_code}")
            print(f"Ответ сервера: {e.response.text}\n")
            
            if user_id and user_id in db["users"]:
                db["users"][user_id] += 1
                save_db(db)
            return {"reply": "*Персонаж на мгновение замолчал... (Ошибка связи с нейросетью, попробуйте еще раз)*"}
            
        except Exception as e:
            print(f"\n[!!!] СИСТЕМНАЯ ОШИБКА В CHAT [!!!]: {str(e)}\n")
            
            if user_id and user_id in db["users"]:
                db["users"][user_id] += 1
                save_db(db)
            return {"reply": "*Персонаж на мгновение замолчал... (Внутренняя ошибка сервера, попробуйте еще раз)*"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


html

<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
<title>Hakka AI</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{
--accent:#ff8c00;
--bg:#050506;
--card:rgba(255,255,255,0.03);
--border:rgba(255,255,255,0.08);
--star-color: #f7a800;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}

body{margin:0;font-family:-apple-system,sans-serif;background:var(--bg);color:white;height:100vh;overflow:hidden;position:relative; touch-action: manipulation; -webkit-text-size-adjust: 100%;}
body::before{content:"";position:fixed;top:-20%;left:-20%;width:60%;height:60%;background:radial-gradient(circle,rgba(255,140,0,0.35) 0%,transparent 70%);filter:blur(90px);z-index:-1;}
header{padding:16px;text-align:center;font-weight:800;background:rgba(0,0,0,0.6);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.05);box-shadow:0 0 10px rgba(255,140,0,0.2);}

#loading-screen {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: var(--bg); z-index: 9999;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}
#loading-screen img {
  width: 200px; max-width: 70%; border-radius: 25px;
  box-shadow: 0 0 40px rgba(255, 140, 0, 0.5); margin-bottom: 30px;
  animation: pulseLogo 2s infinite;
}
.progress-container {
  width: 60%; height: 6px; background: rgba(255,255,255,0.1);
  border-radius: 10px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
#loading-progress {
  width: 0%; height: 100%; background: linear-gradient(90deg, #ff8c00, #ffb347);
  box-shadow: 0 0 10px rgba(255,140,0,0.8); transition: width 0.1s linear;
}
@keyframes pulseLogo {
  0% { transform: scale(0.95); box-shadow: 0 0 20px rgba(255,140,0,0.2); }
  50% { transform: scale(1.02); box-shadow: 0 0 40px rgba(255,140,0,0.6); }
  100% { transform: scale(0.95); box-shadow: 0 0 20px rgba(255,140,0,0.2); }
}

#hero-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding-bottom: 20px;
}
.hero-card {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: 18px 12px; background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.01));
  border-radius: 24px; border: 1px solid rgba(255,255,255,0.05);
  cursor: pointer; transition: .3s; position: relative; backdrop-filter: blur(10px);
}
.hero-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(255,140,0,0.3); border-color: rgba(255,140,0,0.4); }
.hero-avatar {
  width: 75px; height: 75px; border-radius: 22px; background-size: cover; background-position: center;
  border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 0 15px rgba(255,140,0,0.15); margin-bottom: 12px; flex-shrink: 0;
}
.hero-name { font-weight: 800; font-size: 14px; width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
.hero-cat { font-size: 11px; color: var(--accent); font-weight: 700; background: rgba(255,140,0,0.1); padding: 4px 10px; border-radius: 8px; }

#toast-container {
  position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
  z-index: 10000; display: flex; flex-direction: column; gap: 10px; pointer-events: none;
}
.toast {
  background: rgba(15, 15, 18, 0.95); border: 1px solid var(--accent);
  box-shadow: 0 5px 25px rgba(255,140,0,0.3); color: white; padding: 14px 20px;
  border-radius: 16px; font-weight: 700; font-size: 13px; text-align: center;
  animation: toastIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
@keyframes toastIn { from { opacity: 0; transform: translateY(-30px) scale(0.9); } to { opacity: 1; transform: translateY(0) scale(1); } }

.screen{display:none;flex-direction:column;height:100%;overflow-y:auto;padding:20px 20px 90px;animation:fadeScreen .35s ease;}
.screen.active{display:flex;}
@keyframes fadeScreen{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.chat-msgs{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:12px;padding-bottom:90px;}

.bubble{
  padding:12px 16px; border-radius:18px; max-width:85%; background:#1a1a1c; 
  animation:msgIn .25s ease; word-break:break-word; line-height:1.4;
  cursor: pointer; -webkit-user-select: none; user-select: none; -webkit-touch-callout: none;
}
.bubble-user{background:var(--accent);color:black;font-weight:600;}
@keyframes msgIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

.vulgar-active {
  animation: pulseVulgar 1.5s infinite !important;
  background: linear-gradient(135deg, #ff3b3b, #ff8c00) !important;
  color: white !important;
  box-shadow: 0 0 15px rgba(255, 59, 59, 0.6) !important;
}
@keyframes pulseVulgar {
  0% { transform: scale(1); box-shadow: 0 0 10px rgba(255,59,59,0.4); }
  50% { transform: scale(1.05); box-shadow: 0 0 25px rgba(255,59,59,0.8); }
  100% { transform: scale(1); box-shadow: 0 0 10px rgba(255,59,59,0.4); }
}

.modern-input{width:100%;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:16px;color:white;margin-bottom:12px;outline:none;font-family:inherit;}
.btn{ background: linear-gradient(135deg, #ff8c00, #ffb347); border:none; padding:16px; border-radius:18px; font-weight:800; cursor:pointer; color:black; transition:.3s; box-shadow:0 5px 15px rgba(255,140,0,.4); font-family:inherit; }
.btn:hover{ transform:scale(1.05); box-shadow:0 0 25px rgba(255,140,0,.8); }
.nav-bar{position:fixed;bottom:0;left:0;right:0;height:70px;background:rgba(10,10,12,0.9);border-top:1px solid rgba(255,255,255,0.05);display:flex;backdrop-filter:blur(20px);box-shadow:0 -5px 20px rgba(255,140,0,0.1);z-index: 100;}
.nav-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;color:#555;font-weight:700;transition:.2s;font-size:9px;gap:4px;}
.nav-item .icon {font-size:22px; margin-bottom:2px; transition:.2s;}
.nav-item:active{transform:scale(.9);}
.nav-item.active{color:var(--accent);text-shadow:0 0 10px rgba(255,140,0,0.7);}
.nav-item.active .icon {filter: drop-shadow(0 0 5px rgba(255,140,0,0.8));}
.typing-bubble{display:flex;gap:5px;align-items:center;padding:12px 16px;border-radius:18px;background:#1a1a1c;width:60px;}
.typing-dot{width:6px;height:6px;background:#aaa;border-radius:50%;animation:typingBounce 1s infinite;}
.typing-dot:nth-child(2){animation-delay:.2s;}
.typing-dot:nth-child(3){animation-delay:.4s;}
@keyframes typingBounce{0%{transform:translateY(0)}40%{transform:translateY(-6px)}80%{transform:translateY(0)}100%{transform:translateY(0)}}
#chat-input-box{display:flex;gap:10px;align-items:center;padding:10px;position:sticky;bottom:70px;background:rgba(5,5,6,0.9);backdrop-filter:blur(10px);}
#chat-input-box input{padding:14px 16px;}
#chat-input-box button{padding:14px 18px;}
select.modern-input option {background-color: #1a1a1c; color: white;}

.modal-overlay { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); backdrop-filter:blur(5px); z-index:999; align-items:center; justify-content:center; padding:20px; animation:fadeScreen .2s ease; }
.modal-content { background:var(--bg); border:1px solid var(--border); border-radius:20px; padding:20px; max-width:400px; width:100%; position:relative; box-shadow:0 0 30px rgba(255,140,0,0.15); }
.close-btn { position:absolute; top:15px; right:15px; cursor:pointer; color:#888; font-size:20px; transition:.2s; }
.close-btn:hover { color:var(--accent); }

.day-dot { width: 26px; height: 26px; border-radius: 8px; background: #222; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: #555; border: 1px solid var(--border); }
.day-dot.active { background: var(--accent); color: black; border-color: var(--accent); box-shadow: 0 0 10px rgba(255,140,0,0.5); }
.day-dot.past { background: #ffb347; color: black; opacity: 0.7; }

/* Кастомный ползунок */
input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 18px; width: 18px; border-radius: 50%; background: var(--accent); cursor: pointer; margin-top: -7px; box-shadow: 0 0 10px rgba(255,140,0,0.8); }
input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; cursor: pointer; background: rgba(255,255,255,0.2); border-radius: 2px; }
</style>
</head>
<body>

<div id="toast-container"></div>

<div id="loading-screen">
  <img src="https://i.ibb.co/SDwJ00zt/IMG-20260405-140342-085.jpg" alt="Hakka AI Loading">
  <div class="progress-container">
    <div id="loading-progress"></div>
  </div>
</div>

<header id="h-title" style="position:relative;">
  HAKKA AI
  <div id="token-count" style="position:absolute; right:15px; top:50%; transform:translateY(-50%); background:rgba(255,140,0,0.2); padding:4px 10px; border-radius:12px; font-size:14px; color:var(--accent); border:1px solid rgba(255,140,0,0.3); display:flex; align-items:center; gap:5px; box-shadow:0 0 10px rgba(255,140,0,0.1); cursor:default;">
    🪙 <span id="token-val">100</span>
  </div>
</header>

<div id="scr-heroes" class="screen active">
<div style="display:flex; gap:10px; margin-bottom:15px;">
  <input id="search-input" class="modern-input" style="margin-bottom:0;" placeholder="Поиск персонажа" oninput="renderHeroes()">
  <button class="btn" style="padding: 16px; border-radius: 16px; flex-shrink: 0;" onclick="toggleFilters()">Фильтры</button>
</div>

<div id="filter-modal" style="display:none; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 15px; margin-bottom: 15px; backdrop-filter: blur(10px); animation: fadeScreen .2s ease;">
  <div style="font-weight: 800; margin-bottom: 12px; color: var(--accent); text-align: center;">Выберите категорию:</div>
  <div style="display:flex; gap: 10px;">
    <button class="btn" style="flex:1; padding: 10px;" onclick="setFilter('all')">Все</button>
    <button class="btn" style="flex:1; padding: 10px;" onclick="setFilter('Аниме')">Аниме</button>
    <button class="btn" style="flex:1; padding: 10px;" onclick="setFilter('Игры')">Игры</button>
  </div>
</div>

<div id="hero-list"></div>
</div>

<div id="scr-chat" class="screen">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;padding-bottom:10px;border-bottom:1px solid var(--border);">
    <div onclick="nav('scr-heroes')" style="color:var(--accent);cursor:pointer;font-size:24px;">⬅</div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div id="chat-header-avatar" class="hero-avatar" style="width:36px;height:36px;border-radius:10px;margin-bottom:0;"></div>
      <div id="chat-hero-name" style="font-weight:800;font-size:16px;">ЧАТ</div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <button id="btn-vulgar" class="btn" style="padding:6px 10px; border-radius:10px; font-size:14px; background: #222; color: #aaa;" onclick="toggleVulgarMode()">🔞</button>
      <button class="btn" style="padding:6px 10px; border-radius:10px; font-size:14px;" onclick="showInfoModal()">ℹ️</button>
      <div onclick="clearChat()" style="color:#ff3b3b;cursor:pointer;font-size:12px;font-weight:bold;background:rgba(255,59,59,0.1);padding:6px 10px;border-radius:10px;">ОЧИСТИТЬ</div>
    </div>
  </div>
  <div id="chat-messages" class="chat-msgs"></div>
  <div id="chat-input-box">
    <input id="chat-input" class="modern-input" placeholder="Введите сообщение...">
    <button class="btn" onclick="sendMessage()">🚀</button>
  </div>
</div>

<div id="scr-tasks" class="screen">
  <div style="text-align:center;font-weight:800;font-size:20px;margin-bottom:20px;color:var(--accent);">Доступные задания</div>
  <div style="text-align:center;font-size:14px;color:#aaa;margin-bottom:20px;">Выполняй задания и получай бесплатные Хакка Коины!</div>
  <div id="task-list"></div>
</div>

<div id="scr-shop" class="screen">
  <div style="text-align:center;font-weight:800;font-size:20px;margin-bottom:10px;color:var(--accent);">Магазин</div>
  
  <div style="background:var(--card); padding:20px; border-radius:16px; border:1px solid var(--border); margin-bottom: 25px; box-shadow:0 5px 15px rgba(0,0,0,0.2);">
    <div style="font-weight:bold; margin-bottom:10px; color:white; text-align:center;">Активация промокода</div>
    <div style="display:flex; gap:10px;">
      <input id="shop-promo-input" class="modern-input" style="margin-bottom:0; text-transform:uppercase;" placeholder="Введите код">
      <button class="btn" style="padding:16px; border-radius:16px; flex-shrink:0;" onclick="activatePromo()">ОК</button>
    </div>
  </div>

  <div style="text-align:center;font-size:14px;color:#aaa;margin-bottom:25px;">Покупай Хакка Коины за Telegram Stars и общайся без границ!</div>
  <div id="shop-list" style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding-bottom: 20px;"></div>
</div>

<div id="scr-admin" class="screen">
<div id="admin-box" style="display:none">
<div id="admin-form-title" style="text-align:center;font-weight:800;color:var(--accent);margin-bottom:15px;">Создание персонажа</div>
<div style="text-align:center; margin-bottom:20px;">
  <label style="cursor:pointer; display:inline-block;">
    <div id="adm-prev" style="width:100px; height:100px; border-radius:25px; background:var(--card); background-size:cover; background-position:center; border:2px dashed var(--border); display:flex; align-items:center; justify-content:center; color:#555; font-size:12px; margin-bottom:10px;">Нажми <br> загрузить</div>
    <input type="file" id="adm-file" style="display:none" accept="image/*" onchange="previewHeroImg(event)">
  </label>
</div>
<input id="adm-name" class="modern-input" placeholder="Имя персонажа">
<select id="adm-category" class="modern-input">
  <option value="Аниме">Аниме</option>
  <option value="Игры">Игры</option>
</select>
<textarea id="adm-desc" class="modern-input" style="height:120px;" placeholder="Описание/Промпт (характер персонажа)"></textarea>
<button id="admin-submit-btn" class="btn" style="width:100%" onclick="saveHero()">Создать персонажа</button>

<hr style="border-color:var(--border);margin:25px 0;">

<div style="text-align:center;font-weight:800;color:var(--accent);margin-bottom:15px;">Выдача токенов</div>
<input id="adm-token-id" type="number" class="modern-input" placeholder="Telegram ID пользователя">
<input id="adm-token-amount" type="number" class="modern-input" placeholder="Количество токенов">
<select id="adm-token-reason" class="modern-input">
  <option value="admin">Выдать как Администратор</option>
  <option value="donate">Выдать за Донат</option>
</select>
<button class="btn" style="width:100%" onclick="giveTokens()">Выдать токены</button>

<hr style="border-color:var(--border);margin:25px 0;">

<div style="text-align:center;font-weight:800;color:var(--accent);margin-bottom:15px;">Добавить задание</div>
<input id="adm-task-name" class="modern-input" placeholder="Текст задания (например: Подписка на канал)">
<input id="adm-task-link" class="modern-input" placeholder="Ссылка (https://t.me/...)">
<div style="font-size:12px; color:#aaa; margin-bottom:12px; text-align:center;">Награда автоматически составит 10 Хакка Коинов</div>
<button class="btn" style="width:100%" onclick="saveTask()">Опубликовать задание</button>

<hr style="border-color:var(--border);margin:25px 0;">

<div style="text-align:center;font-weight:800;color:var(--accent);margin-bottom:15px;">Создание промокода</div>
<input id="adm-promo-code" class="modern-input" style="text-transform:uppercase;" placeholder="Код (например: HAKKA2026)">
<input id="adm-promo-reward" type="number" class="modern-input" placeholder="Награда (Хакка Коины)">
<input id="adm-promo-uses" type="number" class="modern-input" placeholder="Лимит использований (например: 100)">
<button class="btn" style="width:100%" onclick="createPromo()">Создать промокод</button>

</div>
<div id="no-admin">🔒 доступ закрыт</div>
</div>

<div id="scr-profile" class="screen" style="text-align:center;padding-top:40px;">
  <label style="cursor:pointer;display:block;margin-bottom:15px;">
    <div id="p-avatar" style="width:120px;height:120px;border-radius:30px;background:#222;margin:auto;background-size:cover;background-position:center;"></div>
    <input type="file" id="avatar-upload" style="display:none" accept="image/*" onchange="changeAvatar(event)">
  </label>
  <div style="margin-bottom:8px;font-size:14px;color:#aaa;">Ваш ID:</div>
  <div id="my-id" style="margin-bottom:15px;font-weight:700;font-size:16px;color:var(--accent)">ID: ---</div>

  <div style="margin-bottom:20px;font-weight:700;font-size:16px;color:white;background:rgba(255,255,255,0.05);padding:10px 20px;border-radius:16px;display:inline-block;border:1px solid var(--border);box-shadow:0 0 10px rgba(255,140,0,0.05);">
    Баланс: <span style="color:var(--accent);" id="prof-token-val">100</span> 🪙
  </div>

  <div style="margin-bottom:25px;">
    <div style="font-size:12px; color:#aaa; margin-bottom:8px;">Ваш никнейм в чате:</div>
    <input id="user-nickname" class="modern-input" style="width:240px;margin:auto;text-align:center;padding:12px;" placeholder="Введите никнейм" oninput="updateNickname(this.value)">
  </div>

  <div id="user-role" style="margin-top:6px;margin-bottom:15px;font-size:13px"></div>

  <div style="background:var(--card); padding:20px; border-radius:16px; border:1px solid var(--border); margin-top: 15px; box-shadow:0 5px 15px rgba(0,0,0,0.2); text-align: center;">
    <div style="font-weight:bold; margin-bottom:10px; color:white; font-size: 18px;">Реферальная программа</div>
    <div style="font-size:13px; color:#aaa; margin-bottom:15px;">
      Приглашай друзей и получай <b style="color:var(--accent)">35 🪙</b> за каждого, кто запустит бота и войдет в приложение!
    </div>
    <div onclick="copyRefLink()" style="background: rgba(0,0,0,0.5); border: 1px dashed var(--accent); padding: 12px; border-radius: 12px; font-family: monospace; color: var(--accent); font-size: 14px; word-break: break-all; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: .2s;">
      <span id="ref-link-display">Загрузка ссылки...</span>
      <span style="font-size: 18px;">📋</span>
    </div>
    <div style="font-size: 11px; color: #777; margin-top: 8px;">Нажмите на ссылку, чтобы скопировать</div>
  </div>

</div>

<div id="scr-settings" class="screen">
  <div style="text-align:center;font-weight:800;font-size:20px;margin-bottom:25px;color:var(--accent);">Настройки чата</div>
  
  <div style="background:var(--card); padding:20px; border-radius:16px; border:1px solid var(--border); margin-bottom: 15px;">
    <div style="font-weight:bold; margin-bottom:10px; color:white;">Отображение действий (Roleplay)</div>
    <div style="font-size:12px; color:#aaa; margin-bottom:15px;">Как бот будет отыгрывать действия, например: улыбнулась, обняла и т.д.</div>
    <select id="rp-style-select" class="modern-input" style="margin-bottom:0;" onchange="saveRpStyle()">
      <option value="asterisks">Обычные звёздочки (*улыбнулась*)</option>
      <option value="italic_dark">Без звёздочек (курсив и тёмный текст)</option>
    </select>
  </div>

  <div style="background:var(--card); padding:20px; border-radius:16px; border:1px solid var(--border);">
    <div style="font-weight:bold; margin-bottom:10px; color:white;">Размер ответа ИИ</div>
    <div style="font-size:14px; color:var(--accent); font-weight: bold; margin-bottom:15px; text-align: center;" id="response-size-label">Средний</div>
    <input type="range" id="response-size-slider" min="1" max="3" step="1" value="2" style="margin-bottom:15px;" oninput="saveResponseSize()">
    <div style="display:flex; justify-content:space-between; font-s

