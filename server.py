import os
import logging
import socket
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import threading

# -------- CONFIG --------
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET = os.getenv("SECRET") or "123456"
MAC = os.getenv("MAC") or "9C:6B:00:4C:FA:B3"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

current_command = None
last_result = "нема"

# -------- KEYBOARD --------
def get_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🖥 Увімкнути ПК"),
        KeyboardButton("🎮 Steam")
    )
    kb.add(
        KeyboardButton("📋 Процеси"),
        KeyboardButton("❌ Вимкнути ПК")
    )
    return kb

# -------- WOL --------
def wake_on_lan(mac):
    mac = mac.replace(":", "").replace("-", "")
    data = bytes.fromhex("FF" * 6 + mac * 16)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(data, ("255.255.255.255", 9))

# -------- API --------
@app.route("/get_command")
def get_command():
    global current_command
    key = request.args.get("key")

    if key != SECRET:
        return jsonify({"cmd": None})

    cmd = current_command
    current_command = None
    return jsonify({"cmd": cmd})

@app.route("/result", methods=["POST"])
def result():
    global last_result
    data = request.json

    if data.get("key") == SECRET:
        last_result = data.get("result")

    return jsonify({"ok": True})

# -------- TELEGRAM --------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Керуй ПК 👇", reply_markup=get_keyboard())

@dp.message_handler(lambda m: m.text == "🖥 Увімкнути ПК")
async def wake_btn(msg: types.Message):
    wake_on_lan(MAC)
    await msg.answer("⚡ ПК вмикається")

@dp.message_handler(lambda m: m.text == "🎮 Steam")
async def steam(msg: types.Message):
    global current_command
    current_command = "steam"
    await msg.answer("🎮 Запускаю Steam")

@dp.message_handler(lambda m: m.text == "❌ Вимкнути ПК")
async def shutdown(msg: types.Message):
    global current_command
    current_command = "shutdown"
    await msg.answer("💤 Вимикаю ПК")

@dp.message_handler(lambda m: m.text == "📋 Процеси")
async def tasks(msg: types.Message):
    global current_command, last_result
    current_command = "tasks"
    await msg.answer("⏳ Отримую список...")
    await msg.answer(last_result or "нема")

# -------- COMMANDS --------
@dp.message_handler(commands=["restart"])
async def restart(msg: types.Message):
    global current_command
    current_command = "restart"
    await msg.answer("🔄 Перезапуск")

@dp.message_handler(commands=["kill"])
async def kill(msg: types.Message):
    global current_command
    name = msg.get_args()
    current_command = f"kill {name}"
    await msg.answer(f"❌ Закриваю {name}")

# -------- RUN --------
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
