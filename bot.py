from flask import Flask, request
import telegram
import os
import asyncio
import threading
from telegram.ext import Application, CommandHandler, ContextTypes
from pybit.unified_trading import HTTP

app = Flask(__name__)

# ================== НАСТРОЙКИ ==================
TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

bot = telegram.Bot(token=TOKEN)
bybit = HTTP(testnet=False, timeout=30)

# ================== WEBHOOK ДЛЯ TRADINGVIEW ==================
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

# ================== КОМАНДЫ ==================
async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 **Jin Trading Bot** онлайн!\n\nИспользуй /analyze BTC")

async def analyze(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol_input = context.args[0].upper() if context.args else "BTC"
        symbol = symbol_input + "USDT"
        
        data = bybit.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        rows = data["result"]["list"]
        closes = [float(row[4]) for row in rows[::-1]]
        price = closes[0]

        text = f"🔍 **Анализ {symbol}**\n**Цена:** `{price:.4f}`"
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# ================== ЗАПУСК ==================
def run_telegram_bot():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("analyze", analyze))
        print("🤖 Telegram Bot успешно запущен...")
        application.run_polling()
    except Exception as e:
        print("❌ TELEGRAM ERROR:", str(e))

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask Webhook запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)