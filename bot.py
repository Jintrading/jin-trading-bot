import os
import asyncio
import threading

from flask import Flask, request

import telegram
from telegram import Update
from telegram.ext import (
Application,
CommandHandler,
ContextTypes
)

import pandas as pd

from pybit.unified_trading import HTTP

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

=====================================

CONFIG

=====================================

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

if not TOKEN:
raise ValueError(“BOT_TOKEN not found”)

bot = telegram.Bot(token=TOKEN)

bybit = HTTP(
testnet=False,
timeout=30
)

app = Flask(name)

=====================================

FLASK

=====================================

@app.route(”/”)
def home():
return “Jin Trading Bot Online”

@app.route(”/webhook”, methods=[“POST”])
def webhook():

try:
    data = request.get_json()
    if data and "message" in data:
        asyncio.run(
            bot.send_message(
                chat_id=CHAT_ID,
                text=data["message"]
            )
        )
        return "OK", 200
except Exception as e:
    print("WEBHOOK ERROR:", e)
return "ERROR", 500

=====================================

TELEGRAM COMMANDS

=====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

text = (
    "🚀 Jin Trading Bot Online\n\n"
    "Команды:\n"
    "/analyze BTC\n"
    "/status"
)
await update.message.reply_text(text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    "✅ Bot Online\n"
    "📡 Bybit Connected\n"
    "🌐 Webhook Active"
)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

try:
    symbol_input = (
        context.args[0].upper()
        if context.args
        else "BTC"
    )
    symbol = symbol_input + "USDT"
    data = bybit.get_kline(
        category="linear",
        symbol=symbol,
        interval="60",
        limit=200
    )
    rows = data["result"]["list"]
    df = pd.DataFrame(rows)
    df = df.iloc[::-1]
    df["close"] = df[4].astype(float)
    price = df["close"].iloc[-1]
    rsi = RSIIndicator(
        df["close"],
        window=14
    ).rsi().iloc[-1]
    ema20 = EMAIndicator(
        df["close"],
        window=20
    ).ema_indicator().iloc[-1]
    ema50 = EMAIndicator(
        df["close"],
        window=50
    ).ema_indicator().iloc[-1]
    macd = MACD(df["close"])
    macd_value = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    if rsi < 30 and macd_value > macd_signal:
        signal = "🟢 BUY"
    elif rsi > 70 and macd_value < macd_signal:
        signal = "🔴 SELL"
    else:
        signal = "🟡 HOLD"
    text = (
        f"🔍 {symbol}\n\n"
        f"Цена: {price:.4f}\n"
        f"RSI: {rsi:.2f}\n"
        f"EMA20: {ema20:.4f}\n"
        f"EMA50: {ema50:.4f}\n"
        f"MACD: {macd_value:.4f}\n"
        f"MACD Signal: {macd_signal:.4f}\n\n"
        f"{signal}"
    )
    await update.message.reply_text(text)
except Exception as e:
    await update.message.reply_text(
        f"Ошибка:\n{e}"
    )

=====================================

TELEGRAM THREAD

=====================================

def run_telegram():

try:
    application = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )
    application.add_handler(
        CommandHandler(
            "status",
            status
        )
    )
    application.add_handler(
        CommandHandler(
            "analyze",
            analyze
        )
    )
    print("🤖 Telegram started")
    application.run_polling(
        drop_pending_updates=True
    )
except Exception as e:
    print("TELEGRAM ERROR:", e)

=====================================

START

=====================================

if name == “main”:

threading.Thread(
    target=run_telegram,
    daemon=True
).start()
port = int(
    os.environ.get(
        "PORT",
        5000
    )
)
print(f"🌐 Flask started on {port}")
app.run(
    host="0.0.0.0",
    port=port
)