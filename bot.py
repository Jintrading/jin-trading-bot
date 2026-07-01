import os
import ccxt
import pandas as pd
import ta
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получение переменных из Render
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') # Твой ID, куда пересылать сигналы
WEBHOOK_URL = "https://jin-trading-bot.onrender.com"
exchange = ccxt.bybit()

# Имя бота, сообщения которого мы хотим "слушать"
SOURCE_BOT_USERNAME = "gurutrading1bot" 

# --- Функция анализа ---
def get_market_data(symbol_base):
    try:
        symbol = f"{symbol_base.upper()}/USDT"
        bars = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=100)
        df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'close', 'v'])
        
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        last = df.iloc[-1]
        
        return f"📊 <b>{symbol}</b>\nЦена: {last['close']:.4f}\nRSI: {last['rsi']:.2f}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# --- Webhook для Telegram (Прием всех сообщений) ---
@app.route('/telegram-hook', methods=['POST'])
def telegram_hook():
    update = request.json
    
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        
        # 1. Если сообщение от другого бота - пересылаем его тебе
        if 'from' in msg and msg['from'].get('username') == SOURCE_BOT_USERNAME:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": f"🔔 Сигнал от {SOURCE_BOT_USERNAME}:\n{text}"})

        # 2. Если команда от тебя
        if text.startswith('/analyze'):
            parts = text.split()
            symbol = parts[1] if len(parts) > 1 else "BTC"
            result = get_market_data(symbol)
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": chat_id, "text": result, "parse_mode": "HTML"})
            
    return "OK", 200

# --- Webhook для TradingView ---
@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    data = request.json
    msg = data.get('message', 'Сигнал получен')
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": f"🔔 {msg}"})
    return "OK", 200

if __name__ == '__main__':
    # Привязка вебхука
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/telegram-hook")
    app.run(host='0.0.0.0', port=5000)
