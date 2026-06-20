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

# ================== TELEGRAM КОМАНДЫ ==================
async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **Jin Trading Bot** онлайн!\n\n"
        "Доступные команды:\n"
        "/analyze BTC — анализ монеты\n"
        "/status — статус бота\n"
        "/help — список команд"
    )

async def analyze(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol_input = context.args[0].upper() if context.args else "BTC"
        symbol = symbol_input + "USDT"
        
        data = bybit.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        df = pd.DataFrame(data["result"]["list"])
        df = df.iloc[::-1]
        df["close"] = df[4].astype(float)
        df["volume"] = df[5].astype(float)

        price = df["close"].iloc[-1]
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]
        ema20 = EMAIndicator(df["close"], window=20).ema_indicator().iloc[-1]

        text = f"""
🔍 **Анализ {symbol}**

**Цена:** `{price:.4f}`
**RSI:** `{rsi:.2f}`
**EMA20:** `{ema20:.4f}`

**Сигнал:** {'🟢 STRONG BUY' if rsi < 35 else '🟡 WAIT' if rsi < 50 else '🔴 NO TRADE'}
"""
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка анализа: {e}")

async def status(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает\n🌐 Webhook активен\n📡 Bybit подключён")

async def help_command(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 **Доступные команды:**\n\n"
        "/start — приветствие\n"
        "/analyze BTC — анализ монеты\n"
        "/status — статус бота\n"
        "/help — этот список"
    )

# ================== ЗАПУСК ==================
def run_telegram_bot():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("analyze", analyze))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("help", help_command))
        
        print("🤖 Telegram Bot успешно запущен...")
        application.run_polling()
    except Exception as e:
        print("❌ TELEGRAM ERROR:", str(e))

if __name__ == "__main__":
    # Запускаем Telegram в отдельном потоке
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # Запускаем Flask webhook
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask Webhook запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)