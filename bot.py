import os
import ccxt
import pandas as pd
import ta
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# Получение переменных из Render
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
exchange = ccxt.bybit()

# Функция анализа данных
def get_market_data(symbol_base):
    try:
        symbol = f"{symbol_base.upper()}/USDT"
        bars = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        last = df.iloc[-1]
        
        return (f"📊 <b>Анализ {symbol}</b>\n\n"
                f"Цена: {last['close']:.4f}\n"
                f"RSI: {last['rsi']:.2f}\n"
                f"EMA20: {last['ema20']:.4f}\n"
                f"EMA50: {last['ema50']:.4f}\n"
                f"MACD: {last['macd']:.4f}")
    except Exception as e:
        return f"Ошибка получения данных: {str(e)}"

# --- Telegram Bot ---
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0] if context.args else "BTC"
    result = get_market_data(symbol)
    await update.message.reply_text(result, parse_mode='HTML')

def run_telegram_bot():
    if TOKEN:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("analyze", analyze_command))
        application.run_polling()

# --- Webhooks (TradingView & Health) ---
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook активен и ждет данные от TradingView", 200
    
    data = request.json
    msg = data.get('message', 'Сигнал получен')
    
    # Отправка в Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": f"🔔 {msg}", "parse_mode": "HTML"})
    return jsonify({"status": "success"}), 200

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    # Запуск бота в потоке
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000)
