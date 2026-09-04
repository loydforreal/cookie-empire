import json
import os
import math
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

DATA_FILE = "save.json"
ADMIN_NICKNAME = "boss"

AVAILABLE_SKINS = {
    "default": {"name": "Классика", "icon": "🍪", "req_rebirths": 0, "mult": 1.0},
    "donut": {"name": "Неоновый пончик", "icon": "🍩", "req_rebirths": 2, "mult": 1.5},
    "pizza": {"name": "Кибер-пицца", "icon": "🍕", "req_rebirths": 5, "mult": 2.5},
    "diamond": {"name": "Алмазный кристалл", "icon": "💎", "req_rebirths": 10, "mult": 5.0},
    "crown": {"name": "Корона Повелителя", "icon": "👑", "req_rebirths": 20, "mult": 12.0},
    "singularity": {"name": "Сингулярность", "icon": "🌌", "req_rebirths": 35, "mult": 30.0},
}

BASE_UPGRADES_CONFIG = {
    "cursor": {"name": "Двойной клик (+1)", "cost": 8, "power": 1, "cost_mult": 1.08, "max_level": 100},
    "finger": {"name": "Мега-палец (+5)", "cost": 30, "power": 5, "cost_mult": 1.10, "max_level": 80},
    "oven": {"name": "Бабушкина духовка (+25)", "cost": 120, "power": 25, "cost_mult": 1.12, "max_level": 60},
    "farm": {"name": "Пшеничная ферма (+60)", "cost": 350, "power": 60, "cost_mult": 1.15, "max_level": 50},
    "factory": {"name": "Кондитерская фабрика (+150)", "cost": 1200, "power": 150, "cost_mult": 1.17, "max_level": 45},
    "mine": {"name": "Сахарная шахта (+400)", "cost": 4000, "power": 400, "cost_mult": 1.19, "max_level": 40},
    "bank": {"name": "Печеньковый банк (+1.2K)", "cost": 15000, "power": 1200, "cost_mult": 1.21, "max_level": 35},
    "quantum": {"name": "Квантовый генератор (+3.5K)", "cost": 60000, "power": 3500, "cost_mult": 1.23, "max_level": 30},
    "station": {"name": "Орбитальная пекарня (+10K)", "cost": 250000, "power": 10000, "cost_mult": 1.25, "max_level": 25},
    "collider": {"name": "Коллайдер теста (+35K)", "cost": 1200000, "power": 35000, "cost_mult": 1.27, "max_level": 20},
    "portal": {"name": "Врата измерений (+120K)", "cost": 6000000, "power": 120000, "cost_mult": 1.29, "max_level": 15},
    "synthesizer": {"name": "Синтезатор Вселенных (+500K)", "cost": 35000000, "power": 500000, "cost_mult": 1.32, "max_level": 10},
}

ARTIFACTS_POOL = {
    "sugar_compass": {
        "name": "Сахарный компас", "icon": "🧭", "rarity": "Обычный", "color": "#8b949e", "type": "cookie_mult", "val": 1.5,
        "desc": "+50% ко всем печенькам"
    },
    "butter_knife": {
        "name": "Золотая лопатка", "icon": "🧈", "rarity": "Редкий", "color": "#58a6ff", "type": "cookie_mult", "val": 2.5,
        "desc": "x2.5 к силе клика"
    },
    "baker_heart": {
        "name": "Сердце пекарни", "icon": "💖", "rarity": "Эпический", "color": "#bc8cff", "type": "cookie_mult", "val": 5.0,
        "desc": "x5.0 к силе клика"
    },
    "infinity_flour": {
        "name": "Бесконечная мука", "icon": "✨", "rarity": "Легендарный", "color": "#f0883e", "type": "cookie_mult", "val": 12.0,
        "desc": "x12.0 к силе клика"
    },
    "reborn_amulet": {
        "name": "Амулет кармы", "icon": "🧿", "rarity": "Редкий", "color": "#58a6ff", "type": "rebirth_discount", "val": 0.20,
        "desc": "-20% к цене перерождений"
    },
    "hourglass": {
        "name": "Часы судьбы", "icon": "⏳", "rarity": "Эпический", "color": "#bc8cff", "type": "rebirth_discount", "val": 0.40,
        "desc": "-40% к цене перерождений"
    },
    "phoenix_feather": {
        "name": "Перо Феникса", "icon": "🪶", "rarity": "Легендарный", "color": "#f0883e", "type": "rebirth_discount", "val": 0.60,
        "desc": "-60% к цене перерождений"
    }
}

BOXES_CONFIG = {
    "wooden": {
        "name": "Деревянный ящик",
        "icon": "📦",
        "cost": 1,
        "weights": [40, 30, 15, 5, 8, 2, 0]
    },
    "ether": {
        "name": "Эфирный ящик",
        "icon": "🔮",
        "cost": 3,
        "weights": [10, 15, 30, 20, 10, 10, 5]
    }
}

QUIZ_QUESTIONS = [
    {
        "q": "Вопрос 1/3: Что делать, если тесто внезапно осознало себя как личность?",
        "options": [
            "Вызвать экзорциста",
            "Быстрее отправить в духовку, пока оно не создало профсоюз",
            "Начать с ним философский диспут"
        ],
        "correct": 1
    },
    {
        "q": "Вопрос 2/3: Бабушка предлагает ещё одну печеньку, но ты уже съел 4 000 000. Твои действия?",
        "options": [
            "Сказать, что на диете",
            "Открыть рот и сказать 'Спасибо, бабуль'",
            "Позвонить в полицию"
        ],
        "correct": 1
    },
    {
        "q": "Вопрос 3/3: В чём главный смысл бытия печеньки?",
        "options": [
            "Стать крошками на клавиатуре в 3 часа ночи",
            "Принести гармонию во вселенную",
            "Быть проданной за перерождение"
        ],
        "correct": 0
    }
]

def get_base_upgrades():
    res = {}
    for k, v in BASE_UPGRADES_CONFIG.items():
        res[k] = {
            "name": v["name"],
            "cost": v["cost"],
            "power": v["power"],
            "cost_mult": v["cost_mult"],
            "count": 0,
            "max_level": v["max_level"]
        }
    return res

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

users_data = load_data()

def get_player_artifact_bonuses(player: dict):
    cookie_mult = 1.0
    rebirth_discount = 0.0
    for art_id in player.get("artifacts", []):
        art = ARTIFACTS_POOL.get(art_id)
        if not art:
            continue
        if art["type"] == "cookie_mult":
            cookie_mult *= art["val"]
        elif art["type"] == "rebirth_discount":
            rebirth_discount = max(rebirth_discount, art["val"])
    return cookie_mult, rebirth_discount

def get_rebirth_cost(player: dict) -> int:
    base_cost = int(800 * (2.3 ** player["rebirths"]))
    _, discount = get_player_artifact_bonuses(player)
    final_cost = int(base_cost * (1.0 - discount))
    return max(200, final_cost)

def sync_active_skin(player: dict):
    active_key = player.get("active_skin", "default")
    skin_data = AVAILABLE_SKINS.get(active_key, AVAILABLE_SKINS["default"])
    if player["rebirths"] < skin_data["req_rebirths"]:
        player["active_skin"] = "default"
        return True
    return False

def calculate_effective_power(player: dict) -> int:
    sync_active_skin(player)
    base = player["click_power"]
    rebirth_mult = player["rebirths"] + 1
    skin_key = player.get("active_skin", "default")
    skin_data = AVAILABLE_SKINS.get(skin_key, AVAILABLE_SKINS["default"])
    
    skin_mult = skin_data["mult"]
    artifact_cookie_mult, _ = get_player_artifact_bonuses(player)

    return max(1, math.floor(base * rebirth_mult * skin_mult * artifact_cookie_mult))

def ensure_user(user: str):
    user = (user or "").strip()
    if not user:
        user = "Player"
    if user not in users_data:
        users_data[user] = {
            "cookies": 0,
            "click_power": 1,
            "rebirths": 0,
            "active_skin": "default",
            "artifacts": [],
            "autoclicker_unlocked": False,
            "upgrades": get_base_upgrades()
        }
        save_data()
    else:
        p = users_data[user]
        if "active_skin" not in p or p.get("active_skin") not in AVAILABLE_SKINS:
            p["active_skin"] = "default"
        if "artifacts" not in p:
            p["artifacts"] = []
        if "autoclicker_unlocked" not in p:
            p["autoclicker_unlocked"] = False
        sync_active_skin(p)
        for k, v in BASE_UPGRADES_CONFIG.items():
            if k not in p["upgrades"]:
                p["upgrades"][k] = {
                    "name": v["name"],
                    "cost": v["cost"],
                    "power": v["power"],
                    "cost_mult": v["cost_mult"],
                    "count": 0,
                    "max_level": v["max_level"]
                }
            else:
                p["upgrades"][k]["max_level"] = v["max_level"]
                p["upgrades"][k]["cost_mult"] = v["cost_mult"]
    return user

def compute_bulk_purchase(item: dict, current_cookies: int, mode: str):
    count = item["count"]
    max_lvl = item["max_level"]
    multiplier = item.get("cost_mult", 1.15)
    available_levels = max(0, max_lvl - count)

    if available_levels == 0:
        return 0, 0, False, True

    cost = item["cost"]
    total_cost = 0
    count_to_buy = 0

    mode_str = str(mode).lower()
    if mode_str in ["1", "10", "100"]:
        target = min(int(mode_str), available_levels)
        for _ in range(target):
            total_cost += cost
            cost = max(cost + 1, int(cost * multiplier))
            count_to_buy += 1
        can_afford = current_cookies >= total_cost and count_to_buy > 0
        return count_to_buy, total_cost, can_afford, False
    elif mode_str == "max":
        rem_cookies = current_cookies
        next_cost = cost
        while rem_cookies >= next_cost and count_to_buy < available_levels:
            rem_cookies -= next_cost
            total_cost += next_cost
            count_to_buy += 1
            next_cost = max(next_cost + 1, int(next_cost * multiplier))
        if count_to_buy == 0:
            return 1, cost, False, False
        return count_to_buy, total_cost, True, False

    return 1, item["cost"], current_cookies >= item["cost"], False

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookie Empire</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .container {
            display: flex;
            gap: 24px;
            align-items: stretch;
            justify-content: center;
            flex-wrap: wrap;
            max-width: 860px;
        }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 14px;
            padding: 24px;
            width: 320px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        h2 {
            margin-top: 0;
            margin-bottom: 16px;
            color: #58a6ff;
            text-align: center;
            font-size: 20px;
        }
        .input-group {
            margin-bottom: 12px;
        }
        label {
            display: block;
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 4px;
        }
        .nick-box {
            display: flex;
            gap: 6px;
        }
        input {
            flex: 1;
            padding: 8px 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #fff;
            font-size: 14px;
            box-sizing: border-box;
            outline: none;
        }
        input:focus {
            border-color: #58a6ff;
        }
        .nick-save-btn {
            padding: 0 14px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #58a6ff;
            font-weight: 700;
            cursor: pointer;
        }
        .nick-save-btn:hover {
            background: #30363d;
        }
        .cookie-stage {
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 140px;
            margin: 4px 0;
        }
        .cookie-btn {
            font-size: 82px;
            background: none;
            border: none;
            cursor: pointer;
            outline: none;
            user-select: none;
            transition: transform 0.08s ease;
            padding: 0;
            z-index: 2;
        }
        .cookie-btn:active {
            transform: scale(0.88);
        }
        .cookie-btn:hover {
            transform: scale(1.05);
        }
        .floating-particle {
            position: absolute;
            pointer-events: none;
            font-weight: 700;
            font-size: 22px;
            color: #f0883e;
            user-select: none;
            z-index: 10;
            display: flex;
            align-items: center;
            gap: 4px;
            animation: flyUp 0.8s ease-out forwards;
        }
        @keyframes flyUp {
            0% {
                opacity: 1;
                transform: translate(-50%, 0) scale(0.8);
            }
            100% {
                opacity: 0;
                transform: translate(-50%, -100px) scale(1.2);
            }
        }
        .stats-box {
            background: #0d1117;
            border: 1px dashed #30363d;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            margin-bottom: 12px;
        }
        .stats-label {
            font-size: 12px;
            color: #8b949e;
        }
        .stats-number {
            font-size: 28px;
            font-weight: 700;
            color: #f0883e;
            margin: 2px 0;
        }
        .stats-sub {
            display: flex;
            justify-content: space-around;
            font-size: 12px;
            margin-top: 4px;
        }
        .power-badge {
            color: #3fb950;
            font-weight: 600;
        }
        .rebirth-badge {
            color: #a371f7;
            font-weight: 600;
        }
        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .action-btn {
            width: 100%;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
        }
        .shop-btn {
            background-color: #238636;
            color: #fff;
        }
        .shop-btn:hover {
            background-color: #2ea043;
        }
        .box-btn {
            background-color: #d29922;
            color: #0d1117;
        }
        .box-btn:hover {
            background-color: #e3b341;
        }
        .autoclicker-btn {
            background-color: #30363d;
            color: #c9d1d9;
            border-color: #484f58;
        }
        .autoclicker-btn.unlocked {
            background-color: #1f6feb;
            color: #fff;
            border-color: #388bfd;
        }
        .autoclicker-btn.active {
            background-color: #238636;
            color: #fff;
            border-color: #2ea043;
        }
        .skin-btn {
            background-color: #8957e5;
            color: #fff;
        }
        .skin-btn:hover {
            background-color: #a371f7;
        }
        .rebirth-btn {
            background-color: #bf8700;
            color: #fff;
        }
        .rebirth-btn:hover:not(:disabled) {
            background-color: #d4a72c;
        }
        .rebirth-btn:disabled {
            background-color: #21262d;
            color: #484f58;
            cursor: not-allowed;
            border-color: #30363d;
        }
        .leaderboard-list {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex-grow: 1;
        }
        .leader-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: #0d1117;
            border: 1px solid #21262d;
            border-radius: 6px;
            font-size: 14px;
            gap: 8px;
        }
        .leader-rank {
            color: #58a6ff;
            font-weight: 700;
            margin-right: 6px;
        }
        .leader-info-left {
            display: flex;
            align-items: center;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .leader-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            text-align: right;
            margin-left: auto;
        }
        .leader-score {
            color: #3fb950;
            font-weight: 600;
            display: block;
        }
        .leader-rebirths {
            font-size: 11px;
            color: #a371f7;
        }
        .admin-action-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 2px 4px;
            border-radius: 4px;
            transition: all 0.15s ease;
        }
        .edit-user-btn {
            color: #58a6ff;
        }
        .edit-user-btn:hover {
            background: #388bfd22;
        }
        .delete-user-btn {
            color: #f85149;
        }
        .delete-user-btn:hover {
            background: #da363322;
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            backdrop-filter: blur(4px);
        }
        .modal-overlay.open {
            display: flex;
        }
        .modal-content {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            width: 90%;
            max-width: 540px;
            padding: 22px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.8);
            max-height: 85vh;
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .modal-title {
            font-size: 18px;
            font-weight: 700;
            color: #58a6ff;
        }
        .close-btn {
            background: none;
            border: none;
            color: #8b949e;
            font-size: 20px;
            cursor: pointer;
        }

        .modal-scrollable {
            overflow-y: auto;
            padding-right: 6px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .modal-scrollable::-webkit-scrollbar {
            width: 6px;
        }
        .modal-scrollable::-webkit-scrollbar-track {
            background: #0d1117;
            border-radius: 4px;
        }
        .modal-scrollable::-webkit-scrollbar-thumb {
            background: #30363d;
            border-radius: 4px;
        }
        .modal-scrollable::-webkit-scrollbar-thumb:hover {
            background: #58a6ff;
        }

        .bulk-bar {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }
        .bulk-selector {
            display: flex;
            flex: 1;
            gap: 6px;
            background: #0d1117;
            padding: 4px;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        .bulk-btn {
            flex: 1;
            padding: 6px 0;
            background: transparent;
            border: none;
            color: #8b949e;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .bulk-btn:hover {
            color: #c9d1d9;
        }
        .bulk-btn.active {
            background: #21262d;
            color: #58a6ff;
            border: 1px solid #30363d;
        }

        .autobuy-btn {
            padding: 8px 12px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            color: #8b949e;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }
        .autobuy-btn.active {
            background: #388bfd22;
            color: #58a6ff;
            border-color: #58a6ff;
        }

        .list-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            gap: 10px;
        }
        .row-title {
            font-size: 14px;
            font-weight: 600;
            color: #c9d1d9;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .row-cost {
            font-size: 13px;
            color: #f0883e;
            margin-top: 2px;
        }
        .row-desc {
            font-size: 12px;
            color: #58a6ff;
            font-weight: 600;
            margin-top: 2px;
        }
        .row-progress {
            font-size: 11px;
            color: #8b949e;
            margin-top: 2px;
        }
        .modal-btn {
            padding: 8px 14px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #58a6ff;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
        }
        .modal-btn:hover:not(:disabled) {
            background: #58a6ff;
            color: #0d1117;
        }
        .modal-btn.active-skin {
            background: #238636;
            color: #fff;
            border-color: #238636;
            cursor: default;
        }
        .modal-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        .box-open-btn {
            background-color: #d29922;
            color: #0d1117;
            border-color: #d29922;
        }
        .box-open-btn:hover:not(:disabled) {
            background-color: #e3b341;
            color: #0d1117;
        }

        .info-sub-btn {
            padding: 8px 10px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #8b949e;
            font-size: 12px;
            cursor: pointer;
        }
        .info-sub-btn:hover {
            color: #c9d1d9;
            border-color: #58a6ff;
        }

        .inventory-badge {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
        }

        .chances-container {
            display: none;
            background: #0d1117;
            border: 1px dashed #30363d;
            border-radius: 8px;
            padding: 10px;
            margin-top: 4px;
        }
        .chance-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            border-bottom: 1px solid #161b22;
            font-size: 12px;
        }
        .chance-item:last-child {
            border-bottom: none;
        }

        .quiz-card {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .quiz-title {
            font-size: 15px;
            font-weight: 700;
            color: #c9d1d9;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        .quiz-option {
            display: block;
            width: 100%;
            text-align: left;
            padding: 10px 14px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 13px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .quiz-option:hover {
            border-color: #58a6ff;
            background: #21262d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>Cookie Empire</h2>
            
            <div class="input-group">
                <label>Ваш никнейм</label>
                <div class="nick-box">
                    <input type="text" id="username" value="Player" maxlength="12" onkeydown="if(event.key==='Enter') commitUsername();">
                    <button class="nick-save-btn" onclick="commitUsername()">OK</button>
                </div>
            </div>

            <div class="cookie-stage" id="stage">
                <button class="cookie-btn" id="cookie" onclick="clickCookie(event)">🍪</button>
            </div>

            <div class="stats-box">
                <div class="stats-label">Баланс печенек</div>
                <div class="stats-number" id="cookieCount">0</div>
                <div class="stats-sub">
                    <span class="power-badge" id="powerLabel">Клик: +1</span>
                    <span class="rebirth-badge" id="rebirthLabel">Ранг: 0 ✨</span>
                </div>
            </div>

            <div class="btn-group">
                <button class="action-btn shop-btn" onclick="openShop()">🛒 Магазин улучшений</button>
                <button class="action-btn box-btn" onclick="openBoxes()">📦 Ящики с артефактами</button>
                <button class="action-btn autoclicker-btn" id="autoclickerMainBtn" onclick="handleAutoclickerBtn()">🤖 Автокликер (Тест)</button>
                <button class="action-btn skin-btn" onclick="openSkins()">🎨 Гардероб скинов</button>
                <button class="action-btn rebirth-btn" id="rebirthBtn" onclick="doRebirth()">✨ Перерождение</button>
            </div>
        </div>

        <div class="card">
            <h2>🏆 Топ игроков</h2>
            <ul class="leaderboard-list" id="leaderList"></ul>
            <div style="font-size: 11px; color: #8b949e; text-align: center; margin-top: 10px;">
                Обновляется в реальном времени
            </div>
        </div>
    </div>

    <!-- Модалка Магазина -->
    <div class="modal-overlay" id="shopModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Магазин улучшений</div>
                <button class="close-btn" onclick="closeShop()">✕</button>
            </div>
            
            <div class="bulk-bar">
                <div class="bulk-selector">
                    <button class="bulk-btn active" id="btn-1" onclick="setBulk('1')">x1</button>
                    <button class="bulk-btn" id="btn-10" onclick="setBulk('10')">x10</button>
                    <button class="bulk-btn" id="btn-100" onclick="setBulk('100')">x100</button>
                    <button class="bulk-btn" id="btn-max" onclick="setBulk('max')">МАКС</button>
                </div>
                <button class="autobuy-btn" id="autoBuyToggleBtn" onclick="toggleAutoBuy()">⚡ Автопрокачка: ВЫКЛ</button>
            </div>

            <div class="modal-scrollable" id="upgradesList"></div>
        </div>
    </div>

    <!-- Модалка Ящиков -->
    <div class="modal-overlay" id="boxModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">📦 Ящики с артефактами</div>
                <button class="close-btn" onclick="closeBoxes()">✕</button>
            </div>

            <div class="modal-scrollable">
                <div style="font-size: 13px; color: #8b949e; margin-bottom: 4px;">
                    Открывай ящики за перерождения ✨ чтобы получить уникальные артефакты! Нажмите <b>«ℹ️ Шансы»</b> чтобы увидеть таблицу дропа.
                </div>

                <div>
                    <div class="list-row">
                        <div>
                            <div class="row-title">📦 Деревянный ящик</div>
                            <div class="row-cost" style="color: #a371f7;">Стоимость: 1 ✨</div>
                            <div class="row-progress">Шанс: Обычные и Редкие артефакты</div>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <button class="info-sub-btn" onclick="toggleChances('wooden')">ℹ️ Шансы</button>
                            <button class="modal-btn box-open-btn" id="openWoodBtn" onclick="openLootBox('wooden')">Открыть</button>
                        </div>
                    </div>
                    <div class="chances-container" id="chances_wooden"></div>
                </div>

                <div>
                    <div class="list-row">
                        <div>
                            <div class="row-title">🔮 Эфирный ящик</div>
                            <div class="row-cost" style="color: #a371f7;">Стоимость: 3 ✨</div>
                            <div class="row-progress">Высокий шанс: Эпические и Легендарные</div>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <button class="info-sub-btn" onclick="toggleChances('ether')">ℹ️ Шансы</button>
                            <button class="modal-btn box-open-btn" id="openEtherBtn" onclick="openLootBox('ether')">Открыть</button>
                        </div>
                    </div>
                    <div class="chances-container" id="chances_ether"></div>
                </div>

                <div style="margin-top: 14px; font-weight: 700; color: #58a6ff; font-size: 15px;">Ваша коллекция артефактов:</div>
                <div id="artifactsInventory" style="display: flex; flex-direction: column; gap: 6px;"></div>
            </div>
        </div>
    </div>

    <!-- Модалка Теста Автокликера -->
    <div class="modal-overlay" id="quizModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">🎓 Экзамен Почётного Пекаря</div>
                <button class="close-btn" onclick="closeQuiz()">✕</button>
            </div>
            <div class="modal-scrollable">
                <div style="font-size: 13px; color: #8b949e; margin-bottom: 10px;">
                    Докажи искусственному интеллекту, что ты достоин получить бота-автокликера! Ответь правильно на 3 вопроса.
                </div>
                <div id="quizContainer"></div>
            </div>
        </div>
    </div>

    <!-- Модалка Скинов -->
    <div class="modal-overlay" id="skinModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Гардероб скинов</div>
                <button class="close-btn" onclick="closeSkins()">✕</button>
            </div>
            <div class="modal-scrollable" id="skinsList"></div>
        </div>
    </div>

    <script>
        const stage = document.getElementById('stage');
        let currentEffectivePower = 1;
        let currentSkinIcon = '🍪';
        let currentBulk = localStorage.getItem('cookie_bulk') || '1';
        let autoBuyEnabled = false;
        let autoBuyInterval = null;
        let autoclickerUnlocked = false;
        let autoclickerRunning = false;
        let autoclickerInterval = null;
        let currentQuizIndex = 0;

        // Фиксированное имя активной сессии
        let currentActiveUser = localStorage.getItem('cookie_user') || 'Player';

        function formatNumber(num) {
            if (num === null || num === undefined) return '0';
            num = Number(num);
            if (isNaN(num)) return '0';
            if (num < 1000) return Math.floor(num).toLocaleString('en-US');

            const suffixes = [
                { val: 1e33, symbol: "Dc" },
                { val: 1e30, symbol: "No" },
                { val: 1e27, symbol: "Oc" },
                { val: 1e24, symbol: "Sp" },
                { val: 1e21, symbol: "Sx" },
                { val: 1e18, symbol: "Qi" },
                { val: 1e15, symbol: "Qa" },
                { val: 1e12, symbol: "T" },
                { val: 1e9,  symbol: "B" },
                { val: 1e6,  symbol: "M" },
                { val: 1e3,  symbol: "K" }
            ];

            for (let i = 0; i < suffixes.length; i++) {
                if (num >= suffixes[i].val) {
                    const formatted = (num / suffixes[i].val).toFixed(2);
                    return formatted.replace(/\\.00$/, '') + suffixes[i].symbol;
                }
            }
            return num.toString();
        }

        window.addEventListener('DOMContentLoaded', () => {
            document.getElementById('username').value = currentActiveUser;
            if (localStorage.getItem('cookie_autobuy') === 'true') {
                toggleAutoBuy(true);
            }
            updateBulkButtons();
            loadUserData();
            fetchLeaderboard();
        });

        function getUser() {
            return currentActiveUser;
        }

        function commitUsername() {
            const val = document.getElementById('username').value.trim() || 'Player';
            currentActiveUser = val;
            localStorage.setItem('cookie_user', val);
            loadUserData();
            fetchLeaderboard();
        }

        async function loadUserData() {
            try {
                const res = await fetch(`/api/user?user=${encodeURIComponent(getUser())}`);
                const data = await res.json();
                updateDisplay(data);
            } catch (e) {}
        }

        function updateDisplay(data) {
            document.getElementById('cookieCount').innerText = formatNumber(data.cookies);
            document.getElementById('powerLabel').innerText = `Клик: +${formatNumber(data.effective_power)}`;
            document.getElementById('rebirthLabel').innerText = `Ранг: ${data.rebirths} ✨`;
            currentEffectivePower = data.effective_power;

            currentSkinIcon = data.skin_icon || '🍪';
            document.getElementById('cookie').innerText = currentSkinIcon;

            const rebirthBtn = document.getElementById('rebirthBtn');
            rebirthBtn.innerText = `✨ Перерождение (${formatNumber(data.rebirth_cost)} 🍪)`;
            rebirthBtn.disabled = data.cookies < data.rebirth_cost;

            autoclickerUnlocked = !!data.autoclicker_unlocked;
            updateAutoclickerUI();
        }

        function updateAutoclickerUI() {
            const btn = document.getElementById('autoclickerMainBtn');
            if (!autoclickerUnlocked) {
                btn.className = "action-btn autoclicker-btn";
                btn.innerText = "🤖 Автокликер (Пройти тест)";
            } else {
                if (autoclickerRunning) {
                    btn.className = "action-btn autoclicker-btn active";
                    btn.innerText = "🤖 Автокликер: ВКЛ";
                } else {
                    btn.className = "action-btn autoclicker-btn unlocked";
                    btn.innerText = "🤖 Автокликер: ВЫКЛ";
                }
            }
        }

        function handleAutoclickerBtn() {
            if (!autoclickerUnlocked) {
                openQuiz();
            } else {
                autoclickerRunning = !autoclickerRunning;
                if (autoclickerRunning) {
                    if (!autoclickerInterval) {
                        autoclickerInterval = setInterval(runAutoclickerTick, 250);
                    }
                } else {
                    if (autoclickerInterval) {
                        clearInterval(autoclickerInterval);
                        autoclickerInterval = null;
                    }
                }
                updateAutoclickerUI();
            }
        }

        async function runAutoclickerTick() {
            if (!autoclickerRunning) return;
            try {
                const res = await fetch(`/api/click?user=${encodeURIComponent(getUser())}`, { method: 'POST' });
                const data = await res.json();
                updateDisplay(data);
                renderLeaderboard(data.top);

                const cookieEl = document.getElementById('cookie');
                cookieEl.style.transform = 'scale(0.92)';
                setTimeout(() => { cookieEl.style.transform = ''; }, 70);
            } catch (err) {}
        }

        function openQuiz() {
            currentQuizIndex = 0;
            document.getElementById('quizModal').classList.add('open');
            renderQuiz();
        }

        function closeQuiz() {
            document.getElementById('quizModal').classList.remove('open');
        }

        async function renderQuiz() {
            try {
                const res = await fetch('/api/quiz/questions');
                const questions = await res.json();
                const container = document.getElementById('quizContainer');

                if (currentQuizIndex >= questions.length) {
                    const claimRes = await fetch(`/api/quiz/claim?user=${encodeURIComponent(getUser())}`, { method: 'POST' });
                    const data = await claimRes.json();
                    alert("🎉 Поздравляем! Ты сдал экзамен на высший балл и получил Автокликер!");
                    closeQuiz();
                    updateDisplay(data);
                    return;
                }

                const item = questions[currentQuizIndex];
                container.innerHTML = `
                    <div class="quiz-card">
                        <div class="quiz-title">${item.q}</div>
                        ${item.options.map((opt, idx) => `
                            <button class="quiz-option" onclick="submitAnswer(${idx})">${opt}</button>
                        `).join('')}
                    </div>
                `;
            } catch (e) {}
        }

        async function submitAnswer(choiceIdx) {
            try {
                const res = await fetch(`/api/quiz/answer?q_index=${currentQuizIndex}&choice=${choiceIdx}`, { method: 'POST' });
                const data = await res.json();
                if (data.correct) {
                    currentQuizIndex++;
                    renderQuiz();
                } else {
                    alert("❌ Неверно! Попробуй подумать как настоящая печенька.");
                }
            } catch (e) {}
        }

        async function fetchLeaderboard() {
            try {
                const res = await fetch('/api/leaderboard');
                const data = await res.json();
                renderLeaderboard(data);
            } catch (e) {}
        }

        function renderLeaderboard(list) {
            const container = document.getElementById('leaderList');
            container.innerHTML = '';
            const isBoss = getUser() === 'boss';

            if (!list || list.length === 0) {
                container.innerHTML = '<li style="color:#8b949e;text-align:center;font-size:13px;padding:10px;">Пока нет активных игроков</li>';
                return;
            }

            list.forEach((item, index) => {
                const li = document.createElement('li');
                li.className = 'leader-item';

                let adminButtons = '';
                if (isBoss) {
                    adminButtons = `
                        <button class="admin-action-btn edit-user-btn" title="Сменить ник игроку" onclick="renamePlayer('${item.user}')">✏️</button>
                        <button class="admin-action-btn delete-user-btn" title="Удалить игрока" onclick="deletePlayer('${item.user}')">🗑️</button>
                    `;
                }

                li.innerHTML = `
                    <div class="leader-info-left">
                        <span class="leader-rank">#${index + 1}</span> 
                        <span>${item.skin || '🍪'} ${item.user}</span>
                    </div>
                    <div class="leader-meta">
                        <div>
                            <span class="leader-score">${formatNumber(item.score)} 🍪</span>
                            <span class="leader-rebirths">${item.rebirths} ✨</span>
                        </div>
                        ${adminButtons}
                    </div>
                `;
                container.appendChild(li);
            });
        }

        async function renamePlayer(oldUser) {
            const newUser = prompt(`Введите новый ник для игрока "${oldUser}":`, oldUser);
            if (!newUser || newUser.trim() === '' || newUser.trim() === oldUser) return;

            try {
                const res = await fetch(`/api/admin/rename-player?admin_user=${encodeURIComponent(getUser())}&old_user=${encodeURIComponent(oldUser)}&new_user=${encodeURIComponent(newUser.trim())}`, { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    renderLeaderboard(data.top);
                } else {
                    alert(data.detail);
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function deletePlayer(targetUser) {
            if (!confirm(`Вы действительно хотите удалить игрока "${targetUser}" из топа и базы данных?`)) return;

            try {
                const res = await fetch(`/api/admin/delete-player?admin_user=${encodeURIComponent(getUser())}&target_user=${encodeURIComponent(targetUser)}`, { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    renderLeaderboard(data.top);
                } else {
                    alert(data.detail);
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function clickCookie(e) {
            spawnFloatingParticle(e, currentEffectivePower, currentSkinIcon);

            try {
                const res = await fetch(`/api/click?user=${encodeURIComponent(getUser())}`, { method: 'POST' });
                const data = await res.json();
                updateDisplay(data);
                renderLeaderboard(data.top);
            } catch (err) {
                console.error(err);
            }
        }

        function spawnFloatingParticle(e, amount, icon) {
            const rect = stage.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.innerHTML = `<span>+${formatNumber(amount)}</span><span style="font-size: 16px;">${icon}</span>`;
            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;

            stage.appendChild(particle);

            setTimeout(() => {
                particle.remove();
            }, 800);
        }

        async function doRebirth() {
            if (!confirm("Сбросить текущие печеньки и улучшения магазина ради повышения ранга? (Автокликер, скины и артефакты остаются)")) return;

            try {
                const res = await fetch(`/api/rebirth?user=${encodeURIComponent(getUser())}`, { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    updateDisplay(data);
                    renderLeaderboard(data.top);
                }
            } catch (e) {}
        }

        function updateBulkButtons() {
            document.querySelectorAll('.bulk-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`btn-${currentBulk}`);
            if (activeBtn) activeBtn.classList.add('active');
        }

        function setBulk(mode) {
            currentBulk = mode;
            localStorage.setItem('cookie_bulk', mode);
            updateBulkButtons();
            renderShop();
        }

        function openShop() {
            document.getElementById('shopModal').classList.add('open');
            renderShop();
        }
        function closeShop() {
            document.getElementById('shopModal').classList.remove('open');
        }
        async function renderShop() {
            try {
                const res = await fetch(`/api/shop?user=${encodeURIComponent(getUser())}&mode=${currentBulk}`);
                const data = await res.json();
                const list = document.getElementById('upgradesList');
                list.innerHTML = '';

                for (const [key, item] of Object.entries(data.upgrades)) {
                    const el = document.createElement('div');
                    el.className = 'list-row';

                    let btnText = `Купить +${item.bulk_count}`;
                    let isBtnDisabled = !item.can_afford || item.bulk_count === 0;

                    if (item.is_max) {
                        btnText = 'MAX УР.';
                        isBtnDisabled = true;
                    }

                    el.innerHTML = `
                        <div>
                            <div class="row-title">${item.name} (${item.count}/${item.max_level})</div>
                            <div class="row-cost">${item.is_max ? 'Максимальный уровень' : 'Стоимость: ' + formatNumber(item.bulk_cost) + ' 🍪'}</div>
                        </div>
                        <button class="modal-btn" ${isBtnDisabled ? 'disabled' : ''} onclick="buyUpgrade('${key}', '${currentBulk}')">
                            ${btnText}
                        </button>
                    `;
                    list.appendChild(el);
                }
            } catch (e) {}
        }

        async function buyUpgrade(key, bulkMode) {
            const mode = bulkMode || currentBulk;
            try {
                const res = await fetch(`/api/buy?user=${encodeURIComponent(getUser())}&upgrade_id=${key}&mode=${mode}`, { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    updateDisplay(data);
                    renderShop();
                    fetchLeaderboard();
                }
            } catch (e) {}
        }

        function toggleAutoBuy(forceState) {
            if (forceState !== undefined) {
                autoBuyEnabled = forceState;
            } else {
                autoBuyEnabled = !autoBuyEnabled;
            }

            localStorage.setItem('cookie_autobuy', autoBuyEnabled);
            const btn = document.getElementById('autoBuyToggleBtn');

            if (autoBuyEnabled) {
                btn.innerText = "⚡ Автопрокачка: ВКЛ";
                btn.classList.add('active');
                if (!autoBuyInterval) {
                    autoBuyInterval = setInterval(runAutoBuyTick, 1000);
                }
            } else {
                btn.innerText = "⚡ Автопрокачка: ВЫКЛ";
                btn.classList.remove('active');
                if (autoBuyInterval) {
                    clearInterval(autoBuyInterval);
                    autoBuyInterval = null;
                }
            }
        }

        async function runAutoBuyTick() {
            if (!autoBuyEnabled) return;
            try {
                const res = await fetch(`/api/auto-buy?user=${encodeURIComponent(getUser())}&mode=${currentBulk}`, { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    if (data.bought) {
                        updateDisplay(data);
                        if (document.getElementById('shopModal').classList.contains('open')) {
                            renderShop();
                        }
                    }
                }
            } catch (e) {}
        }

        function openBoxes() {
            document.getElementById('boxModal').classList.add('open');
            renderBoxes();
        }
        function closeBoxes() {
            document.getElementById('boxModal').classList.remove('open');
        }
        async function renderBoxes() {
            try {
                const res = await fetch(`/api/boxes?user=${encodeURIComponent(getUser())}`);
                const data = await res.json();

                document.getElementById('openWoodBtn').disabled = data.rebirths < 1;
                document.getElementById('openEtherBtn').disabled = data.rebirths < 3;

                renderChancesTable('wooden', data.loot_tables.wooden);
                renderChancesTable('ether', data.loot_tables.ether);

                const inv = document.getElementById('artifactsInventory');
                inv.innerHTML = '';

                if (data.artifacts.length === 0) {
                    inv.innerHTML = `<div style="color: #8b949e; font-size: 12px;">У вас пока нет артефактов. Откройте ящик!</div>`;
                } else {
                    data.artifacts.forEach(a => {
                        const div = document.createElement('div');
                        div.className = 'inventory-badge';
                        div.innerHTML = `
                            <span>${a.icon} <b>${a.name}</b> <span style="font-size: 11px; color: ${a.color};">[${a.rarity}]</span></span>
                            <span style="color: #3fb950; font-weight: 600;">${a.desc}</span>
                        `;
                        inv.appendChild(div);
                    });
                }
            } catch (e) {}
        }

        function renderChancesTable(boxId, list) {
            const cont = document.getElementById(`chances_${boxId}`);
            cont.innerHTML = '';
            list.forEach(it => {
                const row = document.createElement('div');
                row.className = 'chance-item';
                row.innerHTML = `
                    <span>${it.icon} ${it.name} <span style="color: ${it.color};">(${it.rarity})</span>: <i>${it.desc}</i></span>
                    <b style="color: #58a6ff;">${it.chance}%</b>
                `;
                cont.appendChild(row);
            });
        }

        function toggleChances(boxId) {
            const el = document.getElementById(`chances_${boxId}`);
            el.style.display = el.style.display === 'block' ? 'none' : 'block';
        }

        async function openLootBox(boxType) {
            try {
                const res = await fetch(`/api/boxes/open?user=${encodeURIComponent(getUser())}&box_type=${boxType}`, { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    alert(`🎉 Получен артефакт: ${data.item.icon} ${data.item.name} (${data.item.rarity})!\nБонус: ${data.item.desc}`);
                    updateDisplay(data);
                    renderBoxes();
                    fetchLeaderboard();
                } else {
                    alert(data.detail);
                }
            } catch (e) {}
        }

        function openSkins() {
            document.getElementById('skinModal').classList.add('open');
            renderSkins();
        }
        function closeSkins() {
            document.getElementById('skinModal').classList.remove('open');
        }
        async function renderSkins() {
            try {
                const res = await fetch(`/api/skins?user=${encodeURIComponent(getUser())}`);
                const data = await res.json();
                const list = document.getElementById('skinsList');
                list.innerHTML = '';

                for (const [key, item] of Object.entries(data.skins)) {
                    const el = document.createElement('div');
                    el.className = 'list-row';

                    let actionBtn = '';
                    if (item.is_active) {
                        actionBtn = `<button class="modal-btn active-skin">Надето</button>`;
                    } else if (item.unlocked) {
                        actionBtn = `<button class="modal-btn" onclick="equipSkin('${key}')">Надеть</button>`;
                    } else {
                        actionBtn = `<button class="modal-btn" disabled>Закрыто</button>`;
                    }

                    const progressText = item.unlocked 
                        ? `<span style="color: #3fb950;">✓ Разблокировано</span>` 
                        : `Требуется: ${item.req_rebirths} ✨ (у вас ${data.rebirths})`;

                    el.innerHTML = `
                        <div>
                            <div class="row-title" style="font-size: 16px;">${item.icon} ${item.name}</div>
                            <div class="row-desc">Множитель: x${item.mult} к клику</div>
                            <div class="row-progress">${progressText}</div>
                        </div>
                        ${actionBtn}
                    `;
                    list.appendChild(el);
                }
            } catch (e) {}
        }
        async function equipSkin(key) {
            try {
                const res = await fetch(`/api/skins/equip?user=${encodeURIComponent(getUser())}&skin_id=${key}`, { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    updateDisplay(data);
                    renderSkins();
                    fetchLeaderboard();
                }
            } catch (e) {}
        }

        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.remove('open');
            });
        });
    </script>
</body>
</html>
"""

def get_current_leaderboard():
    # Отфильтровываем пустые аккаунты без очков и перерождений
    valid_players = [
        (u, d) for u, d in users_data.items() 
        if d.get("cookies", 0) > 0 or d.get("rebirths", 0) > 0
    ]
    sorted_top = sorted(valid_players, key=lambda x: (x[1]["rebirths"], x[1]["cookies"]), reverse=True)[:5]
    top_list = []
    for u, d in sorted_top:
        sync_active_skin(d)
        icon = AVAILABLE_SKINS.get(d.get("active_skin", "default"), {}).get("icon", "🍪")
        top_list.append({"user": u, "score": d["cookies"], "rebirths": d["rebirths"], "skin": icon})
    return top_list

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/user")
def get_user_info(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    effective_power = calculate_effective_power(p)
    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")
    return {
        "cookies": p["cookies"],
        "effective_power": effective_power,
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "autoclicker_unlocked": p.get("autoclicker_unlocked", False)
    }

@app.get("/api/leaderboard")
def get_leaderboard():
    return get_current_leaderboard()

@app.post("/api/click")
def register_click(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    effective_power = calculate_effective_power(p)
    p["cookies"] += effective_power
    save_data()

    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")

    return {
        "cookies": p["cookies"],
        "effective_power": effective_power,
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "autoclicker_unlocked": p.get("autoclicker_unlocked", False),
        "top": get_current_leaderboard()
    }

@app.post("/api/rebirth")
def rebirth(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    cost = get_rebirth_cost(p)

    if p["cookies"] < cost:
        raise HTTPException(status_code=400, detail="Недостаточно печенек для перерождения")

    p["rebirths"] += 1
    p["cookies"] = 0
    p["click_power"] = 1
    p["upgrades"] = get_base_upgrades()
    sync_active_skin(p)
    save_data()

    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")

    return {
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "top": get_current_leaderboard()
    }

@app.get("/api/shop")
def get_shop(user: str = "Player", mode: str = "1"):
    user = ensure_user(user)
    p = users_data[user]
    upgrades_view = {}

    for key, item in p["upgrades"].items():
        count_to_buy, total_cost, can_afford, is_max = compute_bulk_purchase(item, p["cookies"], mode)
        upgrades_view[key] = {
            "name": item["name"],
            "count": item["count"],
            "max_level": item["max_level"],
            "bulk_count": count_to_buy,
            "bulk_cost": total_cost,
            "can_afford": can_afford,
            "is_max": is_max
        }

    return {
        "cookies": p["cookies"],
        "upgrades": upgrades_view
    }

@app.post("/api/buy")
def buy_upgrade(user: str = "Player", upgrade_id: str = "", mode: str = "1"):
    user = ensure_user(user)
    p = users_data[user]

    if upgrade_id not in p["upgrades"]:
        raise HTTPException(status_code=400, detail="Улучшение не найдено")

    upg = p["upgrades"][upgrade_id]
    count_to_buy, total_cost, can_afford, is_max = compute_bulk_purchase(upg, p["cookies"], mode)

    if is_max:
        raise HTTPException(status_code=400, detail="Достигнут максимальный уровень")

    if not can_afford or count_to_buy == 0:
        raise HTTPException(status_code=400, detail="Недостаточно печенек")

    p["cookies"] -= total_cost
    p["click_power"] += upg["power"] * count_to_buy
    upg["count"] += count_to_buy
    
    multiplier = upg.get("cost_mult", 1.15)
    current_cost = upg["cost"]
    for _ in range(count_to_buy):
        current_cost = max(current_cost + 1, int(current_cost * multiplier))
    upg["cost"] = current_cost
    
    save_data()

    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")

    return {
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "autoclicker_unlocked": p.get("autoclicker_unlocked", False)
    }

@app.post("/api/auto-buy")
def auto_buy(user: str = "Player", mode: str = "1"):
    user = ensure_user(user)
    p = users_data[user]

    bought_any = False
    for k, upg in p["upgrades"].items():
        count_to_buy, total_cost, can_afford, is_max = compute_bulk_purchase(upg, p["cookies"], mode)
        if not is_max and can_afford and count_to_buy > 0:
            p["cookies"] -= total_cost
            p["click_power"] += upg["power"] * count_to_buy
            upg["count"] += count_to_buy

            multiplier = upg.get("cost_mult", 1.15)
            current_cost = upg["cost"]
            for _ in range(count_to_buy):
                current_cost = max(current_cost + 1, int(current_cost * multiplier))
            upg["cost"] = current_cost
            bought_any = True

    if not bought_any:
        return {"bought": False}

    save_data()
    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")

    return {
        "bought": True,
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "autoclicker_unlocked": p.get("autoclicker_unlocked", False)
    }

@app.get("/api/quiz/questions")
def get_quiz():
    return [{"q": item["q"], "options": item["options"]} for item in QUIZ_QUESTIONS]

@app.post("/api/quiz/answer")
def check_answer(q_index: int, choice: int):
    if q_index < 0 or q_index >= len(QUIZ_QUESTIONS):
        raise HTTPException(status_code=400, detail="Неверный вопрос")
    is_correct = QUIZ_QUESTIONS[q_index]["correct"] == choice
    return {"correct": is_correct}

@app.post("/api/quiz/claim")
def claim_autoclicker(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    p["autoclicker_unlocked"] = True
    save_data()

    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")
    return {
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "autoclicker_unlocked": True
    }

@app.get("/api/boxes")
def get_boxes_info(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    arts = [ARTIFACTS_POOL[aid] for aid in p.get("artifacts", []) if aid in ARTIFACTS_POOL]

    keys = list(ARTIFACTS_POOL.keys())
    loot_tables = {}

    for b_id, b_conf in BOXES_CONFIG.items():
        total_w = sum(b_conf["weights"])
        b_list = []
        for i, k in enumerate(keys):
            pct = round((b_conf["weights"][i] / total_w) * 100, 1)
            item_meta = ARTIFACTS_POOL[k]
            b_list.append({
                "name": item_meta["name"],
                "icon": item_meta["icon"],
                "rarity": item_meta["rarity"],
                "color": item_meta["color"],
                "desc": item_meta["desc"],
                "chance": pct
            })
        loot_tables[b_id] = b_list

    return {
        "rebirths": p["rebirths"],
        "artifacts": arts,
        "loot_tables": loot_tables
    }

@app.post("/api/boxes/open")
def open_box(user: str = "Player", box_type: str = "wooden"):
    user = ensure_user(user)
    p = users_data[user]

    if box_type not in BOXES_CONFIG:
        raise HTTPException(status_code=400, detail="Неверный тип ящика")

    cost = BOXES_CONFIG[box_type]["cost"]
    if p["rebirths"] < cost:
        raise HTTPException(status_code=400, detail="Недостаточно перерождений для покупки ящика")

    p["rebirths"] -= cost
    sync_active_skin(p)

    keys = list(ARTIFACTS_POOL.keys())
    weights = BOXES_CONFIG[box_type]["weights"]
    chosen_key = random.choices(keys, weights=weights, k=1)[0]

    if chosen_key not in p["artifacts"]:
        p["artifacts"].append(chosen_key)

    save_data()

    skin_icon = AVAILABLE_SKINS.get(p.get("active_skin", "default"), {}).get("icon", "🍪")

    return {
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon,
        "item": ARTIFACTS_POOL[chosen_key]
    }

@app.get("/api/skins")
def get_skins(user: str = "Player"):
    user = ensure_user(user)
    p = users_data[user]
    sync_active_skin(p)
    skins_info = {}
    for key, val in AVAILABLE_SKINS.items():
        is_unlocked = p["rebirths"] >= val["req_rebirths"]
        skins_info[key] = {
            "name": val["name"],
            "icon": val["icon"],
            "mult": val["mult"],
            "req_rebirths": val["req_rebirths"],
            "unlocked": is_unlocked,
            "is_active": key == p.get("active_skin", "default")
        }
    return {"rebirths": p["rebirths"], "skins": skins_info}

@app.post("/api/skins/equip")
def equip_skin(user: str = "Player", skin_id: str = ""):
    user = ensure_user(user)
    p = users_data[user]

    if skin_id not in AVAILABLE_SKINS:
        raise HTTPException(status_code=400, detail="Такого скина не существует")

    req = AVAILABLE_SKINS[skin_id]["req_rebirths"]
    if p["rebirths"] < req:
        raise HTTPException(status_code=400, detail=f"Для этого скина требуется {req} перерождений")

    p["active_skin"] = skin_id
    save_data()

    skin_icon = AVAILABLE_SKINS[skin_id]["icon"]
    return {
        "cookies": p["cookies"],
        "effective_power": calculate_effective_power(p),
        "rebirths": p["rebirths"],
        "rebirth_cost": get_rebirth_cost(p),
        "skin_icon": skin_icon
    }

# --- АДМИН-МЕТОДЫ ---
@app.post("/api/admin/rename-player")
def admin_rename_player(admin_user: str = "", old_user: str = "", new_user: str = ""):
    if admin_user != ADMIN_NICKNAME:
        raise HTTPException(status_code=403, detail="Только boss может переименовывать игроков")

    new_user = new_user.strip()
    if not new_user:
        raise HTTPException(status_code=400, detail="Имя не может быть пустым")

    if old_user not in users_data:
        raise HTTPException(status_code=404, detail="Игрок не найден")

    if new_user in users_data and new_user != old_user:
        raise HTTPException(status_code=400, detail="Игрок с таким именем уже существует")

    users_data[new_user] = users_data.pop(old_user)
    save_data()

    return {"status": "ok", "top": get_current_leaderboard()}

@app.post("/api/admin/delete-player")
def admin_delete_player(admin_user: str = "", target_user: str = ""):
    if admin_user != ADMIN_NICKNAME:
        raise HTTPException(status_code=403, detail="Только boss может удалять игроков")

    if target_user in users_data:
        del users_data[target_user]
        save_data()

    return {"status": "ok", "top": get_current_leaderboard()}

@app.post("/api/admin/set-rebirths")
def admin_set_rebirths(user: str = "Player", count: int = 100):
    user = ensure_user(user)
    p = users_data[user]
    p["rebirths"] = count
    sync_active_skin(p)
    save_data()
    return {"status": "ok", "user": user, "rebirths": p["rebirths"]}