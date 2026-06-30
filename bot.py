import os
import ccxt
import pandas as pd
import ta
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получение переменных из Render
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
WEBHOOK_URL = "https://jin-trading-bot.onrender.com"
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

# --- Webhook для Telegram (Принимает команды /analyze) ---
@app.route('/telegram-hook', methods=['POST'])
def telegram_hook():
    update = request.json
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        
        if text.startswith('/analyze'):
            parts = text.split()
            symbol = parts[1] if len(parts) > 1 else "BTC"
            result = get_market_data(symbol)
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": result, "parse_mode": "HTML"})
    return "OK", 200

# --- Webhook для TradingView ---
@app.route('/webhook', methods=['POST', 'GET'])
def tradingview_webhook():
    if request.method == 'GET':
        return "Webhook активен", 200
    data = request.json
    msg = data.get('message', 'Сигнал получен')
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": f"🔔 {msg}", "parse_mode": "HTML"})
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Привязываем Telegram Webhook к нашему серверу один раз
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/telegram-hook")
    app.run(host='0.0.0.0', port=5000)
