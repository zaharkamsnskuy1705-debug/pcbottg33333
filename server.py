from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os
import socket

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET = "20111705"  # придумай свій

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

current_command = None
last_result = "нема"

# -------- WOL --------
def wake_on_lan("9C:6B:00:4C:FA:B3")
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

# -------- Telegram --------
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Бот працює ✅")

@dp.message_handler(commands=["wake"])
async def wake(msg: types.Message):
    wake_on_lan("AA:BB:CC:DD:EE:FF")  # ← вставиш MAC
    await msg.answer("ПК вмикається ⚡")

@dp.message_handler(commands=["steam"])
async def steam(msg: types.Message):
    global current_command
    current_command = "steam"
    await msg.answer("Запускаю Steam")

@dp.message_handler(commands=["shutdown"])
async def shutdown(msg: types.Message):
    global current_command
    current_command = "shutdown"
    await msg.answer("Вимикаю")

@dp.message_handler(commands=["restart"])
async def restart(msg: types.Message):
    global current_command
    current_command = "restart"
    await msg.answer("Перезапуск")

@dp.message_handler(commands=["tasks"])
async def tasks(msg: types.Message):
    global current_command, last_result
    current_command = "tasks"
    await msg.answer("Чекай...")
    await msg.answer(last_result or "нема")

@dp.message_handler(commands=["kill"])
async def kill(msg: types.Message):
    global current_command
    name = msg.get_args()
    current_command = f"kill {name}"
    await msg.answer(f"Закриваю {name}")

# -------- RUN --------
if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=8080)

    threading.Thread(target=run_flask).start()
    executor.start_polling(dp)