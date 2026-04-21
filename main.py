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
    <div style="display:flex; justify-content:space-between; font-size:11px; color:#777; font-weight: bold;">
      <span style="cursor:pointer;" onclick="document.getElementById('response-size-slider').value=1; saveResponseSize();">Маленький</span>
      <span style="cursor:pointer;" onclick="document.getElementById('response-size-slider').value=2; saveResponseSize();">Средний</span>
      <span style="cursor:pointer;" onclick="document.getElementById('response-size-slider').value=3; saveResponseSize();">Большой</span>
    </div>
  </div>
</div>

<nav class="nav-bar">
  <div class="nav-item active" onclick="nav('scr-heroes',this)">
    <div class="icon">🎭</div><div>Герои</div>
  </div>
  <div class="nav-item" onclick="nav('scr-tasks',this)">
    <div class="icon">🎯</div><div>Задания</div>
  </div>
  <div class="nav-item" onclick="nav('scr-shop',this)">
    <div class="icon">🛒</div><div>Магазин</div>
  </div>
  <div class="nav-item" onclick="nav('scr-admin',this)">
    <div class="icon">👑</div><div>Админ</div>
  </div>
  <div class="nav-item" onclick="nav('scr-profile',this)">
    <div class="icon">👤</div><div>Профиль</div>
  </div>
  <div class="nav-item" onclick="nav('scr-settings',this)">
   <div class="icon">⚙️</div><div>Настр.</div>
  </div>
</nav>

<div id="hero-info-modal" class="modal-overlay">
  <div class="modal-content">
    <div class="close-btn" onclick="document.getElementById('hero-info-modal').style.display='none'">✖</div>
    <div style="display:flex;align-items:center;gap:15px;margin-bottom:15px;">
      <div id="info-modal-avatar" class="hero-avatar" style="width:60px;height:60px;border-radius:16px;margin-bottom:0;"></div>
      <div>
        <h3 style="color:var(--accent);margin:0;font-size:22px;" id="info-modal-name">Имя</h3>
        <span id="info-modal-cat" style="font-size:12px;color:#aaa;background:#222;padding:2px 8px;border-radius:8px;margin-top:4px;display:inline-block;">Категория</span>
      </div>
    </div>
    <div style="font-weight:bold;margin-bottom:8px;color:#fff;">Описание:</div>
    <div id="info-modal-desc" style="color:#ddd;font-size:14px;line-height:1.5;white-space:pre-wrap;max-height:50vh;overflow-y:auto;background:rgba(0,0,0,0.3);padding:12px;border-radius:12px;"></div>
  </div>
</div>

<div id="msg-menu-modal" class="modal-overlay">
  <div class="modal-content" style="text-align:center; padding: 25px 20px;">
    <div class="close-btn" onclick="document.getElementById('msg-menu-modal').style.display='none'">✖</div>
    <div style="font-weight:800;font-size:18px;color:var(--accent);margin-bottom:20px;">Действие с сообщением</div>
    <button class="btn" style="width:100%; margin-bottom: 12px; display:flex; justify-content:center; gap:8px;" onclick="copySelectedMsg()">📋 <span>Скопировать</span></button>
    <button class="btn" style="width:100%; background: rgba(255,59,59,0.1); color: #ff3b3b; border: 1px solid rgba(255,59,59,0.3); box-shadow: none; display:flex; justify-content:center; gap:8px;" onclick="deleteSelectedMsg()">🗑 <span>Удалить</span></button>
  </div>
</div>

<div id="token-modal" class="modal-overlay">
  <div class="modal-content" style="text-align:center;">
    <div class="close-btn" onclick="document.getElementById('token-modal').style.display='none'">✖</div>
    <img src="https://i.gifer.com/xt.gif" style="width:120px; border-radius:20px; margin-bottom:15px; box-shadow:0 0 20px rgba(255,140,0,0.5);">
    <div style="font-weight:800;font-size:20px;color:var(--accent);margin-bottom:10px;">У вас закончились Хакка Коины!</div>
    <div style="color:#ccc;font-size:14px;margin-bottom:20px;">Их можно получить, выполнив бесплатные задания или купив в магазине.</div>
    <button class="btn" style="width:100%; margin-bottom: 10px;" onclick="document.getElementById('token-modal').style.display='none'; nav('scr-tasks'); document.querySelectorAll('.nav-item')[1].classList.add('active'); document.querySelectorAll('.nav-item').forEach(el => {if(el !== document.querySelectorAll('.nav-item')[1]) el.classList.remove('active')});">Перейти в задания</button>
    <button class="btn" style="width:100%; background: #333; color: white;" onclick="document.getElementById('token-modal').style.display='none'; nav('scr-shop'); document.querySelectorAll('.nav-item')[2].classList.add('active'); document.querySelectorAll('.nav-item').forEach(el => {if(el !== document.querySelectorAll('.nav-item')[2]) el.classList.remove('active')});">В магазин</button>
  </div>
</div>

<div id="daily-modal" class="modal-overlay">
  <div class="modal-content" style="text-align:center; padding:30px 20px;">
    <div class="close-btn" onclick="document.getElementById('daily-modal').style.display='none'">✖</div>
    <div style="font-size:50px; margin-bottom:10px;">🎁</div>
    <div style="font-weight:800;font-size:22px;color:var(--accent);margin-bottom:10px;">Ежедневный бонус!</div>
    <div style="color:#ccc;font-size:14px;margin-bottom:20px;">Заходите каждый день и получайте Хакка Коины. Цикл длится 10 дней!</div>
    <div style="display:flex; justify-content:center; gap:8px; margin-bottom:25px; flex-wrap:wrap; padding:0 10px;" id="daily-dots"></div>
    <button class="btn" style="width:100%; font-size:16px;" onclick="claimDailyReward()">Забрать +5 🪙</button>
  </div>
</div>

<script>
document.addEventListener('touchmove', function(event) {
    if (event.touches && event.touches.length > 1) {
        event.preventDefault();
    }
}, { passive: false });

let lastTouchEnd = 0;
document.addEventListener('touchend', function(event) {
    let now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, { passive: false });

const tg = window.Telegram?.WebApp;
const API_URL = "https://elhakka.su"; 
const USER_ROLES = {6625239442:{title:"Владелец проекта",color:"#ff3b3b"},7652697216:{title:"Разработчик",color:"#3b8cff"}};
const ADMIN_IDS = Object.keys(USER_ROLES).map(Number);
const DEFAULT_USER_AVATAR = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='50' height='50' fill='%23aaa'><circle cx='25' cy='25' r='25'/><path d='M25 28c-6 0-11 4-13 10h26c-2-6-7-10-13-10zm0-20a8 8 0 100 16 8 8 0 000-16z' fill='%23333'/></svg>";

const shopPackages = [
  { tokens: 25, stars: 39 },
  { tokens: 100, stars: 63 },
  { tokens: 500, stars: 290 },
  { tokens: 1000, stars: 530 },
  { tokens: 10000, stars: 4800 },
  { tokens: 100000, stars: 39000 }
];

let MY_ID = 0, heroes = [], tasks = [], currentHero = null, selectedIdx = null, tempImg = "", typingElement = null;
let userName = "Пользователь", currentFilter = "all", userCoins = 100, rpStyle = "asterisks", responseSize = 2;
let isVulgarMode = false, selectedMsgId = null, selectedMsgText = "";

function getUKey(key) { return MY_ID + "_" + key; }

function showToast(msg) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerText = msg;
  container.appendChild(toast);
  setTimeout(() => {
     toast.style.opacity = '0';
    toast.style.transform = 'translateY(-30px) scale(0.9)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initTelegram(){
  if(!tg) return;
  tg.ready(); tg.expand();
  if(tg.initDataUnsafe?.user){
    MY_ID = tg.initDataUnsafe.user.id;
    let savedName = localStorage.getItem(getUKey("h_username"));
    userName = savedName ? savedName : (tg.initDataUnsafe.user.first_name || "Пользователь");
    if(!savedName) localStorage.setItem(getUKey("h_username"), userName);
    
    let savedRp = localStorage.getItem(getUKey("h_rp_style"));
    if(savedRp) rpStyle = savedRp;
    else localStorage.setItem(getUKey("h_rp_style"), rpStyle);

    let savedSize = localStorage.getItem(getUKey("h_response_size"));
    if(savedSize) responseSize = parseInt(savedSize);
  }
  initBalance(); updateUI();
}

async function initBalance() {
  if (!MY_ID) return;
  const coinKey = getUKey("h_coins");
  try {
    const r = await fetch(`${API_URL}/api/users/${MY_ID}/balance`);
    if (r.ok) {
        const data = await r.json();
        userCoins = data.tokens;
        localStorage.setItem(coinKey, userCoins);
    }
  } catch(e) {
    if(localStorage.getItem(coinKey) === null) localStorage.setItem(coinKey, 100);
    userCoins = parseInt(localStorage.getItem(coinKey));
  }
  updateTokensUI();
}

// РЕФЕРАЛЬНАЯ ЛОГИКА
function getRefLink() {
  // ВАЖНО: Замените YOUR_BOT_USERNAME на реальный юзернейм вашего бота без @
  return `https://t.me/elhakkachatai_bot?start=${MY_ID || '0'}`;
}

function copyRefLink() {
  const link = getRefLink();
  navigator.clipboard.writeText(link).then(() => {
      showToast("🔗 Реферальная ссылка скопирована!");
      if (window.Telegram?.WebApp?.HapticFeedback) window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
  }).catch(err => showToast("❌ Ошибка копирования"));
}

// Эта функция предназначена для вызова с бэкенда (или через сокеты) 
// когда кто-то успешно зашел по ссылке этого пользователя.
function notifyReferralSuccess() {
  userCoins += 35;
  localStorage.setItem(getUKey("h_coins"), userCoins);
  updateTokensUI();
  showToast("🎉 По вашей ссылке присоединился друг! +35 🪙");
  if (window.Telegram?.WebApp?.HapticFeedback) window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
}
// КОНЕЦ РЕФЕРАЛЬНОЙ ЛОГИКИ

function checkDailyReward() {
  if (!MY_ID) return;
  const todayStr = new Date().toDateString();
  let lastClaim = localStorage.getItem(getUKey('h_daily_date'));
  let streak = parseInt(localStorage.getItem(getUKey('h_daily_streak')) || '0');
  if (lastClaim === todayStr) return; 

  let yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  if (lastClaim !== yesterday.toDateString() && lastClaim !== null) streak = 0; 
  streak++; if(streak > 10) streak = 1; 

  const dotsContainer = document.getElementById('daily-dots'); dotsContainer.innerHTML = '';
  for(let i=1; i<=10; i++) {
      let className = "day-dot" + (i < streak ? " past" : "") + (i === streak ? " active" : "");
      dotsContainer.innerHTML += `<div class="${className}">${i}</div>`;
  }
  document.getElementById('daily-modal').style.display = 'flex';
}

function claimDailyReward() {
  let streak = parseInt(localStorage.getItem(getUKey('h_daily_streak')) || '0');
  let lastClaim = localStorage.getItem(getUKey('h_daily_date'));
  let yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  if (lastClaim !== yesterday.toDateString() && lastClaim !== null) streak = 0;
  streak++; if(streak > 10) streak = 1;

  localStorage.setItem(getUKey('h_daily_date'), new Date().toDateString());
  localStorage.setItem(getUKey('h_daily_streak'), streak);
  
  userCoins += 5; localStorage.setItem(getUKey("h_coins"), userCoins); updateTokensUI();
  document.getElementById('daily-modal').style.display = 'none';
  if (window.Telegram?.WebApp?.HapticFeedback) window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
}

function resetAdminForm() {
  document.getElementById("adm-name").value = ''; document.getElementById("adm-desc").value = ''; document.getElementById("adm-category").value = 'Аниме';
  const prev = document.getElementById("adm-prev"); prev.style.backgroundImage = ''; prev.innerHTML = 'Нажми <br> загрузить'; prev.style.border = '2px dashed var(--border)';
  tempImg = ''; selectedIdx = null; 
  document.getElementById("admin-form-title").innerText = "Создание персонажа"; document.getElementById("admin-submit-btn").innerText = "Создать персонажа";
}

function nav(id,el){
  document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  if(el){ document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active")); el.classList.add("active"); }
  if(id === 'scr-admin' && el) resetAdminForm();
  updateUI();
}

function updateNickname(val) { userName = val.trim() || "Пользователь"; if(MY_ID) localStorage.setItem(getUKey("h_username"), userName); }
function saveRpStyle() { rpStyle = document.getElementById("rp-style-select").value; if(MY_ID) localStorage.setItem(getUKey("h_rp_style"), rpStyle); }
function saveResponseSize() {
  responseSize = parseInt(document.getElementById("response-size-slider").value);
  if(MY_ID) localStorage.setItem(getUKey("h_response_size"), responseSize);
  const labels = {1: "Маленький", 2: "Средний", 3: "Большой"};
  document.getElementById("response-size-label").innerText = labels[responseSize];
}

function escapeHTML(str) { return str.replace(/[&<>'"]/g, tag => ({'&': '&amp;','<': '&lt;','>': '&gt;',"'": '&#39;','"': '&quot;'}[tag])); }
function formatMessage(text, sender) {
  let safeText = escapeHTML(text);
  if (sender === 'bot') {
    if (rpStyle === 'italic_dark') safeText = safeText.replace(/\*(.*?)\*/g, '<i style="color:#888; font-size: 0.95em;">$1</i>');
    else safeText = safeText.replace(/\*(.*?)\*/g, '<i style="color:#ccc;">*$1*</i>');
  }
  return safeText.replace(/\n/g, '<br>');
}

function toggleFilters() {
  const modal = document.getElementById('filter-modal');
  modal.style.display = modal.style.display === 'none' ? 'block' : 'none';
}
function setFilter(category) { currentFilter = category; toggleFilters(); renderHeroes(); }

async function loadHeroes(){
  try{ const r = await fetch(`${API_URL}/api/characters?t=${Date.now()}`); heroes = await r.json(); renderHeroes(); }
  catch(e){console.log("offline heroes", e)}
}

function renderHeroes(){
  const list = document.getElementById("hero-list");
  const isAdm = ADMIN_IDS.includes(Number(MY_ID));
  const searchQuery = document.getElementById("search-input").value.toLowerCase();

  const filteredHeroes = heroes.filter(h => {
    const matchesSearch = h.name.toLowerCase().includes(searchQuery);
    const heroCategory = h.category || 'Аниме';
    return matchesSearch && (currentFilter === 'all' || heroCategory === currentFilter);
  });

  list.innerHTML = filteredHeroes.map((h) => {
    const originalIndex = heroes.indexOf(h);
    const catDisplay = h.category || 'Аниме';
    
    return `
    <div class="hero-card" onclick="openHero(${originalIndex})">
      ${isAdm ? `<div style="position:absolute; top:8px; right:8px; display:flex; gap:6px;">
        <div onclick="editHero(${originalIndex});event.stopPropagation()" style="background:rgba(0,0,0,0.6); padding:6px; border-radius:10px; font-size:12px;">✏️</div>
        <div onclick="deleteHero(${originalIndex});event.stopPropagation()" style="background:rgba(255,59,59,0.4); padding:6px; border-radius:10px; font-size:12px;">🗑</div>
      </div>` : ""}
      <div class="hero-avatar" style="background-image:url(${h.img})"></div>
      <div class="hero-name">${h.name}</div>
      <div class="hero-cat">${catDisplay}</div>
    </div>`
  }).join("");
}

function openHero(i){
  selectedIdx = i; currentHero = heroes[i];
  document.getElementById("chat-hero-name").innerText = currentHero.name;
  document.getElementById("chat-header-avatar").style.backgroundImage = `url(${currentHero.img})`;
  nav("scr-chat"); 
  loadChatHistory(); 
}

function showInfoModal() {
  if(!currentHero) return;
  document.getElementById("info-modal-name").innerText = currentHero.name;
  document.getElementById("info-modal-cat").innerText = currentHero.category || "Аниме";
  document.getElementById("info-modal-desc").innerText = currentHero.desc;
  document.getElementById("info-modal-avatar").style.backgroundImage = `url(${currentHero.img})`;
  document.getElementById("hero-info-modal").style.display = "flex";
}

function toggleVulgarMode() {
    isVulgarMode = !isVulgarMode;
    const btn = document.getElementById("btn-vulgar");
    if(isVulgarMode) {
        btn.classList.add("vulgar-active");
        showToast("🔞 Режим пошлости активирован!");
    } else {
        btn.classList.remove("vulgar-active");
        showToast("😇 Обычный режим");
    }
    loadChatHistory();
}

function getChatHistoryKey() {
    return isVulgarMode ? getUKey('h_chat_v_' + currentHero.name) : getUKey('h_chat_' + currentHero.name);
}

function loadChatHistory() {
  document.getElementById("chat-messages").innerHTML = ""; 
  if(!currentHero || !MY_ID) return;
  const historyStr = localStorage.getItem(getChatHistoryKey());
  if(historyStr) JSON.parse(historyStr).forEach(m => addMsg(m.t, m.s, false, m.id));
}

function showTyping(){
  const c = document.getElementById("chat-messages"); const wrapper = document.createElement("div");
  wrapper.style.display = "flex"; wrapper.style.gap = "10px"; wrapper.style.alignItems = "flex-end";
  const avatarHTML = `<div class="hero-avatar" style="width:30px;height:30px;border-radius:10px;margin-bottom:0;background-image:url(${currentHero ? currentHero.img : ""});"></div>`;
  typingElement = document.createElement("div"); typingElement.className = "typing-bubble";
  typingElement.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
  wrapper.innerHTML = avatarHTML; wrapper.appendChild(typingElement); wrapper.id = "temp-typing";
  c.appendChild(wrapper); c.scrollTop = c.scrollHeight;
}
function hideTyping(){ const t = document.getElementById("temp-typing"); if(t) t.remove(); }
function updateTokensUI() { document.getElementById("token-val").innerText = userCoins; document.getElementById("prof-token-val").innerText = userCoins; }

async function sendMessage(){
  const inp = document.getElementById("chat-input"); const txt = inp.value.trim();
  if(!txt || !currentHero) return;
  if(userCoins <= 0) { document.getElementById("token-modal").style.display = "flex"; return; }
  
  const historyKey = getChatHistoryKey();
  let rawHistory = JSON.parse(localStorage.getItem(historyKey) || "[]");
  
  let formattedHistory = rawHistory.slice(-15).map(m => ({
      role: m.s === 'user' ? 'user' : 'assistant',
      content: m.t
  }));

  const msgId = Date.now().toString();
  addMsg(txt, 'user', true, msgId); 
  inp.value=''; showTyping();

  try{
    const r = await fetch(`${API_URL}/api/chat`,{ 
      method:'POST', 
      headers:{'Content-Type':'application/json'}, 
      body:JSON.stringify({ 
        message: txt, 
        charName: currentHero.name, 
        userId: MY_ID, 
        userName: userName, 
        isVulgar: isVulgarMode,
        history: formattedHistory,      
        responseSize: responseSize      
      }) 
    });
    
    const d = await r.json(); hideTyping();
    if(d && d.reply) {
      userCoins--; if(MY_ID) localStorage.setItem(getUKey("h_coins"), userCoins);
      updateTokensUI(); 
      addMsg(d.reply, 'bot', true, (Date.now() + 1).toString());
    } else addMsg("Ошибка связи (Хакка Коин сохранен)",'bot', false);
  }catch(e){ hideTyping(); addMsg("Ошибка связи (Хакка Коин сохранен)",'bot', false); }
}

function addMsg(t, s, saveToHistory = true, msgId = null) {
  const c = document.getElementById("chat-messages"); const wrapper = document.createElement("div");
  wrapper.style.display = "flex"; wrapper.style.gap = "10px"; wrapper.style.alignItems = "flex-end";
  let avatarUrl = s === 'user' ? (localStorage.getItem(getUKey("user_avatar")) || DEFAULT_USER_AVATAR) : (currentHero ? currentHero.img : "");
  if(s === 'user') wrapper.style.flexDirection = "row-reverse";
  const avatarHTML = `<div class="hero-avatar" style="width:30px;height:30px;border-radius:10px;margin-bottom:0;background-image:url(${avatarUrl});"></div>`;
  const d = document.createElement("div"); d.className = `bubble bubble-${s}`; d.innerHTML = formatMessage(t, s); 
  
  let actualId = msgId || (Date.now().toString() + Math.random().toString());
  
  let pressTimer;
  const startPress = (e) => { 
      pressTimer = setTimeout(() => openMsgMenu(actualId, t), 500); 
  };
  const cancelPress = () => clearTimeout(pressTimer);

  d.addEventListener('touchstart', startPress);
  d.addEventListener('touchend', cancelPress);
  d.addEventListener('touchmove', cancelPress);
  d.addEventListener('mousedown', startPress);
  d.addEventListener('mouseup', cancelPress);
  d.addEventListener('mouseleave', cancelPress);

  wrapper.innerHTML = avatarHTML; wrapper.appendChild(d); c.appendChild(wrapper); c.scrollTop = c.scrollHeight;

  if(saveToHistory && currentHero && MY_ID) {
      const historyKey = getChatHistoryKey();
      const history = JSON.parse(localStorage.getItem(historyKey) || "[]");
      history.push({id: actualId, t: t, s: s}); 
      localStorage.setItem(historyKey, JSON.stringify(history));
  }
}

function openMsgMenu(id, text) {
    if (window.Telegram?.WebApp?.HapticFeedback) window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
    selectedMsgId = id;
    selectedMsgText = text;
    document.getElementById('msg-menu-modal').style.display = 'flex';
}

function copySelectedMsg() {
    navigator.clipboard.writeText(selectedMsgText).then(() => {
        showToast("📋 Сообщение скопировано!");
        document.getElementById('msg-menu-modal').style.display = 'none';
    }).catch(err => showToast("❌ Ошибка копирования"));
}

function deleteSelectedMsg() {
    const historyKey = getChatHistoryKey();
    let history = JSON.parse(localStorage.getItem(historyKey) || "[]");
    history = history.filter(m => m.id !== selectedMsgId);
    localStorage.setItem(historyKey, JSON.stringify(history));
    
    loadChatHistory();
    document.getElementById('msg-menu-modal').style.display = 'none';
    showToast("🗑 Сообщение удалено");
    if (window.Telegram?.WebApp?.HapticFeedback) window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
}

function clearChat(){
  if(!currentHero) return;
  if(confirm("Вы точно хотите очистить историю переписки в этом режиме?")) {
    document.getElementById("chat-messages").innerHTML=""; 
    if(MY_ID) localStorage.removeItem(getChatHistoryKey());
  }
}

async function loadTasks(){
  try{ const r = await fetch(`${API_URL}/api/tasks?t=${Date.now()}`); tasks = await r.json(); renderTasks(); }
  catch(e){console.log("offline tasks", e)}
}

function renderTasks() {
  const list = document.getElementById("task-list"); const isAdm = ADMIN_IDS.includes(Number(MY_ID));
  let completedTasks = MY_ID ? JSON.parse(localStorage.getItem(getUKey("h_completed_tasks")) || "[]") : [];
  if(tasks.length === 0) { list.innerHTML = `<div style="text-align:center;color:#555;margin-top:20px;">Пока нет доступных заданий</div>`; return; }

  list.innerHTML = tasks.map((t, i) => {
    const isDone = completedTasks.includes(i);
    return `
    <div class="hero-card" style="cursor:default;flex-direction:column;align-items:stretch;padding:16px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <b style="font-size:15px; text-align:left;">${t.name}</b>
        <span style="color:var(--accent); font-weight:800; font-size:14px; flex-shrink:0;">+10 🪙</span>
      </div>
      <div style="display:flex; gap:10px;">
        ${isDone ? `<button class="btn" style="flex:1; padding:10px; background:#2a2a2c; color:#777; box-shadow:none; cursor:not-allowed;" disabled>Выполнено</button>` : `<button class="btn" style="flex:1; padding:10px;" onclick="doTask(${i}, '${t.link}')">Выполнить</button>`}
        ${isAdm ? `<button class="btn" style="padding:10px; background:#ff3b3b; box-shadow:none;" onclick="deleteTask(${i})">🗑</button>` : ""}
      </div>
    </div>`;
  }).join("");
}

function doTask(index, link) {
  if(!MY_ID) return;
  let completed = JSON.parse(localStorage.getItem(getUKey("h_completed_tasks")) || "[]");
  if(completed.includes(index)) return;
  if(window.Telegram?.WebApp?.openTelegramLink && link.includes('t.me')) window.Telegram.WebApp.openTelegramLink(link); else window.open(link, '_blank');
  
  setTimeout(() => {
    let freshCompleted = JSON.parse(localStorage.getItem(getUKey("h_completed_tasks")) || "[]");
    if(!freshCompleted.includes(index)) {
      userCoins += 10; localStorage.setItem(getUKey("h_coins"), userCoins);
      freshCompleted.push(index); localStorage.setItem(getUKey("h_completed_tasks"), JSON.stringify(freshCompleted));
      updateTokensUI(); renderTasks(); showToast("✅ Задание выполнено! Начислено 10 Хакка Коинов.");
    }
  }, 2500); 
}

function renderShop() {
  const list = document.getElementById("shop-list");
  list.innerHTML = shopPackages.map(p => `
    <div class="hero-card" style="cursor:default;flex-direction:column;align-items:center;padding:16px;">
      <div style="font-size:32px; margin-bottom:8px;">🪙</div>
      <b style="font-size:20px; color:white; margin-bottom:2px;">${p.tokens}</b>
      <span style="color:#aaa; font-size:11px; margin-bottom:15px; font-weight: bold;">Хакка Коинов</span>
      <button class="btn" style="width:100%; padding:12px; font-size:14px; background: linear-gradient(135deg, #f7bb0e, #f7d54d); color: #000; display: flex; align-items: center; justify-content: center; gap: 4px;" onclick="initPayment(${p.tokens}, ${p.stars})">
        <b>${p.stars}</b> <span style="font-size: 16px;">⭐️</span>
      </button>
    </div>
  `).join("");
}

async function initPayment(tokens, stars) {
  if(!MY_ID) { showToast("Ошибка: Telegram ID не определен!"); return; }
  showToast(`Запрос на покупку ${tokens} 🪙 через Telegram Stars...`);
  try {
    const response = await fetch(`${API_URL}/api/create-stars-invoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: MY_ID, stars: stars, tokens: tokens })
    });
    const data = await response.json();
    if (data.invoice_url) {
      if (window.Telegram?.WebApp?.openInvoice) {
        window.Telegram.WebApp.openInvoice(data.invoice_url, function(status) {
          if (status === 'paid') { showToast("✅ Оплата прошла успешно! Токены зачислены."); initBalance(); } 
          else if (status === 'cancelled') { showToast("❌ Оплата отменена."); } 
          else { showToast("⚠️ Статус оплаты: " + status); }
        });
      } else { window.open(data.invoice_url, '_blank'); }
    } else { showToast("Ошибка создания счета."); }
  } catch(e) { showToast("Ошибка соединения с сервером."); console.error(e); }
}

async function createPromo() {
  const code = document.getElementById("adm-promo-code").value.trim().toUpperCase();
  const reward = parseInt(document.getElementById("adm-promo-reward").value);
  const uses = parseInt(document.getElementById("adm-promo-uses").value);

  if(!code || isNaN(reward) || reward <= 0 || isNaN(uses) || uses <= 0) {
    showToast("Заполните все поля корректно!"); return;
  }

  try {
    await fetch(`${API_URL}/api/promocode/create`, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ adminId: MY_ID, code, reward, uses })
    });
  } catch(e) {}

  let promos = JSON.parse(localStorage.getItem("h_promos") || "{}");
  promos[code] = { reward: reward, uses: uses };
  localStorage.setItem("h_promos", JSON.stringify(promos));

  showToast(`✅ Промокод ${code} на ${reward}🪙 создан (Лимит: ${uses})!`);
  document.getElementById("adm-promo-code").value = "";
  document.getElementById("adm-promo-reward").value = "";
  document.getElementById("adm-promo-uses").value = "";
}

async function activatePromo() {
  const code = document.getElementById("shop-promo-input").value.trim().toUpperCase();
  if(!code) { showToast("Введите промокод!"); return; }
  if(!MY_ID) { showToast("Ошибка авторизации!"); return; }

  let promos = JSON.parse(localStorage.getItem("h_promos") || "{}");
  let activated = JSON.parse(localStorage.getItem(getUKey("h_activated_promos")) || "[]");

  if(activated.includes(code)) {
    showToast("⚠️ Вы уже активировали этот промокод!"); return;
  }

  try {
    const res = await fetch(`${API_URL}/api/promocode/activate`, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ userId: MY_ID, code: code })
    });
    if(res.ok) {
      const data = await res.json();
      userCoins += data.reward; localStorage.setItem(getUKey("h_coins"), userCoins); updateTokensUI();
      activated.push(code); localStorage.setItem(getUKey("h_activated_promos"), JSON.stringify(activated));
      showToast(`✅ Промокод активирован! +${data.reward} 🪙`);
      document.getElementById("shop-promo-input").value = "";
      return;
    }
  } catch(e) {}

  if(promos[code]) {
    if(promos[code].uses <= 0) {
       showToast("❌ Лимит активаций исчерпан!"); return;
    }
    
    userCoins += promos[code].reward;
    localStorage.setItem(getUKey("h_coins"), userCoins);
    updateTokensUI();
    activated.push(code);
    localStorage.setItem(getUKey("h_activated_promos"), JSON.stringify(activated));
    showToast(`✅ Промокод активирован! +${promos[code].reward} 🪙`);
    document.getElementById("shop-promo-input").value = "";
    
    promos[code].uses--;
    if(promos[code].uses <= 0) delete promos[code];
    localStorage.setItem("h_promos", JSON.stringify(promos));
  } else {
    showToast("❌ Неверный или удаленный промокод!");
  }
}

async function giveTokens() {
  const tId = document.getElementById('adm-token-id').value.trim();
  const amt = parseInt(document.getElementById('adm-token-amount').value);
  const reason = document.getElementById('adm-token-reason').value;
  if(!tId || isNaN(amt) || amt <= 0) { showToast("Введите корректный ID и количество!"); return; }
  try {
    const res = await fetch(`${API_URL}/api/give-tokens`, { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ adminId: MY_ID, targetId: parseInt(tId), amount: amt, reason: reason }) 
    });
    if (res.ok) {
        const data = await res.json();
        showToast(`Успешно выдано ${amt} Хакка Коинов пользователю ${tId}!`);
        if (tId == MY_ID) { userCoins = data.new_balance; localStorage.setItem(getUKey("h_coins"), userCoins); updateTokensUI(); }
    } else { showToast("Ошибка доступа! Проверьте ID."); }
  } catch (e) { showToast("Ошибка соединения с сервером."); }
  document.getElementById('adm-token-id').value = ''; document.getElementById('adm-token-amount').value = '';
}

async function saveTask() {
  const name = document.getElementById("adm-task-name").value; const link = document.getElementById("adm-task-link").value;
  if(!name || !link) { alert("Заполни название и ссылку!"); return; }
  const payload = {adminId: MY_ID, task: {name, link}};
  try { await fetch(`${API_URL}/api/tasks`, { method: 'POST', body: JSON.stringify(payload), headers: {'Content-Type': 'application/json'}});
    document.getElementById("adm-task-name").value = ''; document.getElementById("adm-task-link").value = ''; loadTasks(); alert("Задание опубликовано!");
  } catch(e) { alert("Ошибка сохранения задания"); }
}
async function deleteTask(i) {
  if(!confirm("Удалить задание?")) return;
  try { await fetch(`${API_URL}/api/tasks/${i}?adminId=${MY_ID}`, {method: 'DELETE'}); loadTasks(); } catch(e) { alert("Ошибка удаления"); }
}

function previewHeroImg(e){
  const file = e.target.files[0]; if(!file) return;
  const r = new FileReader();
  r.onload = ()=>{
    tempImg = r.result; const prev = document.getElementById("adm-prev");
    prev.style.backgroundImage = `url(${tempImg})`; prev.innerHTML = ''; prev.style.border = 'none';
  }; r.readAsDataURL(file);
}

async function saveHero(){
  const name = document.getElementById("adm-name").value; const desc = document.getElementById("adm-desc").value; const category = document.getElementById("adm-category").value;
  if(!name || !tempImg) { alert("Заполни имя и загрузи фото!"); return; }
  const payload = {adminId:MY_ID, character:{name, desc, img:tempImg, category}};
  if(selectedIdx !== null) payload.index = selectedIdx;
  try {
    await fetch(`${API_URL}/api/characters`,{ method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
    resetAdminForm(); await loadHeroes(); nav('scr-heroes', document.querySelectorAll('.nav-item')[0]);
  } catch(e) { alert("Ошибка сохранения"); }
}

async function deleteHero(i){
  if(!confirm("Удалить персонажа?")) return;
  await fetch(`${API_URL}/api/characters/${i}?adminId=${MY_ID}`,{method:'DELETE'}); loadHeroes();
}

function editHero(i){
  const hero = heroes[i];
  document.getElementById("adm-name").value = hero.name; document.getElementById("adm-desc").value = hero.desc; document.getElementById("adm-category").value = hero.category || 'Аниме';
  tempImg = hero.img; const prev = document.getElementById("adm-prev");
  prev.style.backgroundImage = `url(${tempImg})`; prev.innerHTML = ''; prev.style.border = 'none';
  selectedIdx = i; document.getElementById("admin-form-title").innerText = "Редактирование персонажа"; document.getElementById("admin-submit-btn").innerText = "Сохранить изменения";
  nav("scr-admin"); 
}

function changeAvatar(e){
  const file = e.target.files[0]; if(!file) return;
  const r = new FileReader();
  r.onload = ()=>{
    const img=r.result; if(MY_ID) localStorage.setItem(getUKey("user_avatar"), img); 
    document.getElementById("p-avatar").style.backgroundImage = `url(${img})`;
  }; r.readAsDataURL(file);
}

function updateUI(){
  document.getElementById("my-id").innerText = `ID: ${MY_ID || "---"}`;
  document.getElementById("user-nickname").value = userName;
  document.getElementById("rp-style-select").value = rpStyle;
  
  // Обновляем реферальную ссылку при загрузке ID
  document.getElementById("ref-link-display").innerText = getRefLink();

  document.getElementById("response-size-slider").value = responseSize;
  const labels = {1: "Маленький", 2: "Средний", 3: "Большой"};
  document.getElementById("response-size-label").innerText = labels[responseSize];

  updateTokensUI();
  const roleBox = document.getElementById("user-role");
  if(USER_ROLES[MY_ID]){ const r = USER_ROLES[MY_ID]; roleBox.innerHTML = `<span style="color:${r.color};font-weight:800">${r.title}</span>`; } else roleBox.innerHTML = '';
  const isAdm = ADMIN_IDS.includes(Number(MY_ID));
  document.getElementById("admin-box").style.display = isAdm?"block":"none";
  document.getElementById("no-admin").style.display = isAdm?"none":"block";
  if(MY_ID) {
      const savedAvatar = localStorage.getItem(getUKey("user_avatar"));
      if(savedAvatar) document.getElementById("p-avatar").style.backgroundImage = `url(${savedAvatar})`;
      else document.getElementById("p-avatar").style.backgroundImage = `url(${DEFAULT_USER_AVATAR})`;
  }
}

window.onload = ()=>{
  initTelegram(); loadHeroes(); loadTasks(); renderShop();
  setTimeout(checkDailyReward, 800);
  let prog = 0; let bar = document.getElementById('loading-progress');
  let int = setInterval(() => {
    prog += Math.random() * 20; if(prog > 100) prog = 100; if(bar) bar.style.width = prog + '%';
    if(prog === 100) {
      clearInterval(int);
      setTimeout(() => {
        const loader = document.getElementById('loading-screen');
        if(loader) { loader.style.opacity = '0'; loader.style.visibility = 'hidden'; setTimeout(() => loader.remove(), 500); }
      }, 400);
    }
  }, 150);
}
</script>
</body>
</html>
