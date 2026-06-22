from flask import Flask, request
import os
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from pybit.unified_trading import HTTP
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = 318740554
bybit = HTTP(testnet=False, timeout=30)

# ======================
# FLASK WEBHOOK
# ======================
flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'UNKNOWN')
        signal = data.get('signal', 'UNKNOWN')
        price = data.get('price', 0)
        power = data.get('power', 0)

        message = f"🚨 {symbol} — {signal}\nЦена: {price}\nСила: {power}%"
        Bot(TOKEN).send_message(chat_id=CHAT_ID, text=message)
        return "OK", 200
    except Exception as e:
        print("Webhook error:", e)
        return "Error", 500

# ======================
# ТВОИ КОМАНДЫ
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Trading bot online\n\n/analyze BTC")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper() + "USDT"
        # ... (твой оригинальный код analyze полностью)
        # (я оставил его как был)
        data = bybit.get_kline(category="linear", symbol=symbol, interval="60", limit=200)
        rows = data["result"]["list"]
        df = pd.DataFrame(rows)
        df = df.iloc[::-1]
        df["close"] = df[4].astype(float)
        df["volume"] = df[5].astype(float)
        price = df["close"].iloc[-1]
        rsi = RSIIndicator(df["close"]).rsi().iloc[-1]
        ema20 = EMAIndicator(df["close"], window=20).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(df["close"], window=50).ema_indicator().iloc[-1]
        macd = MACD(df["close"])
        macd_value = macd.macd().iloc[-1]
        macd_signal = macd.macd_signal().iloc[-1]

        # ... (остальной твой код analyze)

        text = f"""...твой текст..."""   # (оставь как было)
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# ======================
# ЗАПУСК
# ======================
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

if __name__ == "__main__":
    import threading
    threading.Thread(target=flask_app.run, kwargs={'host':'0.0.0.0', 'port':int(os.environ.get("PORT", 5000))}, daemon=True).start()
    app.run_polling()
