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

# ================== БРАУЗЕРНЫЕ ТЕСТЫ ==================
@app.route('/start', methods=['GET'])
def start_route():
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text="🚀 Jin Trading Bot работает!"))
    return "OK"

# ================== TELEGRAM КОМАНДЫ ==================
async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Jin Trading Bot онлайн!\n\nИспользуй /analyze BTC")

async def analyze(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol_input = context.args[0].upper() if context.args else "BTC"
        symbol = symbol_input + "USDT"

        await update.message.reply_text(f"🔍 Получаю данные для {symbol}...")

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

        # Volume Force
        buy_volume = 0
        sell_volume = 0
        for i in range(len(df)):
            if df.iloc[i]["close"] >= float(df.iloc[i][1]):
                buy_volume += df.iloc[i]["volume"]
            else:
                sell_volume += df.iloc[i]["volume"]

        total = buy_volume + sell_volume
        buy_force = buy_volume / total * 100 if total > 0 else 0
        sell_force = sell_volume / total * 100 if total > 0 else 0

        # VWAP
        vwap = (df["close"] * df["volume"]).sum() / df["volume"].sum() if df["volume"].sum() > 0 else 0

        # Fibonacci
        high = df["close"].max()
        low = df["close"].min()
        fib_0786 = high - ((high - low) * 0.786)
        fib_1618 = high - ((high - low) * 1.618)

        # Score
        score = 0
        if rsi < 30: score += 1
        if abs(price - fib_0786) / price < 0.02: score += 1
        if macd_value > macd_signal: score += 1
        if buy_force > sell_force: score += 1
        if price > ema20: score += 1

        if score >= 4:
            signal = "🟢 STRONG BUY 🔥"
        elif score >= 3:
            signal = "🟡 GOOD BUY"
        elif score >= 2:
            signal = "🟡 WAIT"
        else:
            signal = "🔴 NO TRADE"

        tp1 = price * 1.012
        tp2 = price * 1.025
        tp3 = price * 1.05
        stop = fib_1618

        text = f"""
🔍 **Анализ {symbol}**

**Цена:** {price:.4f}
**RSI:** {rsi:.2f}
**EMA20:** {ema20:.4f}
**EMA50:** {ema50:.4f}
**MACD:** {macd_value:.4f} | Signal: {macd_signal:.4f}

**Buy Force:** 🟢 {buy_force:.1f}%
**Sell Force:** 🔴 {sell_force:.1f}%
**VWAP:** {vwap:.4f}

**Fib 0.786:** {fib_0786:.4f}
**Fib 1.618:** {fib_1618:.4f}

**SCORE:** {score}/5 → **{signal}**

**TP1:** {tp1:.4f}
**TP2:** {tp2:.4f}
**TP3:** {tp3:.4f}
**STOP:** {stop:.4f}
"""
        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:300]}")

# ================== ЗАПУСК ==================
def run_telegram_bot():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("analyze", analyze))
        print("🤖 Telegram Bot запущен...")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        print("❌ TELEGRAM ERROR:", str(e))

if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask Webhook запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)