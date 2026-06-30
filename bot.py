import os
import ccxt
import pandas as pd
import ta
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)
exchange = ccxt.bybit()

# Функция анализа
def get_market_data(symbol):
    # Получаем свечи
    bars = exchange.fetch_ohlcv(symbol.replace('/', '') + 'USDT', timeframe='4h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Расчет индикаторов
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    last = df.iloc[-1]
    
    # Формируем текст
    res = f"📊 Анализ {symbol}\n\n"
    res += f"Цена: {last['close']:.4f}\n"
    res += f"RSI: {last['rsi']:.2f}\n"
    res += f"EMA20: {last['ema20']:.4f}\n"
    res += f"EMA50: {last['ema50']:.4f}\n"
    res += f"MACD: {last['macd']:.4f}\n"
    res += f"MACD Signal: {last['macd_signal']:.4f}\n"
    return res

# --- Telegram Bot Handler ---
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else "BTC"
    data = get_market_data(symbol)
    await update.message.reply_text(data)

# Запуск бота (в отдельном потоке)
def run_bot():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.run_polling()

import threading
threading.Thread(target=run_bot, daemon=True).start()

# --- Webhook для TradingView ---
@app.route('/webhook', methods=['POST'])
def webhook():
    # Твоя старая логика отправки алертов
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
