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

# Webhook для TradingView
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

# Команды Telegram
async def start(update, context):
    await update.message.reply_text("🚀 Jin Trading Bot онлайн!\n\nИспользуй /analyze BTC")

async def analyze(update, context):
    try:
        symbol = (context.args[0].upper() if context.args else "BTC") + "USDT"
        data = bybit.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        df = pd.DataFrame(data["result"]["list"])
        df = df.iloc[::-1]
        df["close"] = df[4].astype(float)

        price = df["close"].iloc[-1]
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]

        text = f"🔍 **{symbol}**\nЦена: **{price:.4f}**\nRSI: **{rsi:.2f}**"
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    # Запуск Telegram
    def run_telegram():
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("analyze", analyze))
        print("🤖 Telegram Bot запущен...")
        application.run_polling()

    threading.Thread(target=run_telegram, daemon=True).start()

    # Flask будет запущен через gunicorn
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask started on port {port}")