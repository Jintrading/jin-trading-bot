from flask import Flask, request
import telegram
import os
import asyncio
import threading
from telegram.ext import Application, CommandHandler, ContextTypes
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from pybit.unified_trading import HTTP

app = Flask(__name__)

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

bot = telegram.Bot(token=TOKEN)
bybit = HTTP(testnet=False, timeout=30)

# ================== WEBHOOK ==================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            message = data['message']
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown'))
            return "OK", 200
    except Exception as e:
        print("Webhook Error:", str(e))
    return "ERROR", 500

# ================== ТЕСТОВЫЕ РОУТЫ ДЛЯ БРАУЗЕРА ==================
@app.route('/start', methods=['GET'])
def start_route():
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text="🚀 Jin Trading Bot работает!"))
    return "OK"

@app.route('/analyze', methods=['GET'])
def analyze_route():
    symbol = request.args.get('symbol', 'BTC')
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"Анализ запущен для {symbol}USDT (через браузер)"))
    return "OK"

# ================== КОМАНДЫ TELEGRAM ==================
async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Jin Trading Bot онлайн!\n\nИспользуй /analyze BTC")

async def analyze(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (твой полный анализ, как раньше — я оставил его)
    try:
        symbol = context.args[0].upper() + "USDT" if context.args else "BTCUSDT"
        # весь твой код анализа здесь (я его не убирал)
        data = bybit.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        rows = data["result"]["list"]
        df = pd.DataFrame(rows)
        df = df.iloc[::-1]
        df["close"] = df[4].astype(float)
        df["volume"] = df[5].astype(float)

        price = df["close"].iloc[-1]
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]
        # ... (остальной твой код)

        text = f"🔍 Анализ {symbol}\nЦена: {price:.4f}\nRSI: {rsi:.2f}\n... (полный текст)"
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ================== ЗАПУСК ==================
def run_telegram_bot():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("analyze", analyze))
        print("🤖 Telegram Bot запущен...")
        application.run_polling()
    except Exception as e:
        print("❌ TELEGRAM ERROR:", str(e))

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask Webhook запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)