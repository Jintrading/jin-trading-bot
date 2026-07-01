import os
import requests
import ccxt
import pandas as pd
import ta
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
exchange = ccxt.bybit()

def send_tg_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка отправки в ТГ: {e}")

def get_market_data(symbol_base):
    try:
        symbol = f"{symbol_base.upper()}/USDT"
        bars = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=50)
        df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'close', 'v'])
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        last = df.iloc[-1]
        return f"📊 <b>{symbol}</b>\nЦена: {last['close']:.4f}\nRSI: {last['rsi']:.2f}"
    except Exception as e:
        return f"Ошибка анализа: {str(e)}"

# --- 1. Прием команд от тебя (Telegram Webhook) ---
@app.route('/telegram-hook', methods=['POST'])
def telegram_hook():
    data = request.get_json()
    print(f"ЛОГИ TELEGRAM: {data}") # Это покажет в логах Render, что ТГ достучался
    
    if not data or 'message' not in data:
        return "OK", 200
        
    msg = data['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '')
    
    if text.startswith('/analyze'):
        parts = text.split()
        symbol = parts[1] if len(parts) > 1 else "BTC"
        result = get_market_data(symbol)
        send_tg_message(chat_id, result)
        
    return "OK", 200

# --- 2. Прием сигналов от TradingView ---
@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    data = request.get_json()
    if not data:
        return "No data", 400

    symbol = data.get('symbol', 'UNKNOWN')
    signal = data.get('signal', 'Сигнал')
    price = data.get('price', '0')
    power = data.get('power', '0')

    message = (
        f"🚨 <b>TradingView Сигнал</b>\n"
        f"Пара: {symbol}\n"
        f"Сигнал: {signal}\n"
        f"Цена: {price}\n"
        f"Сила: {power}%"
    )
    send_tg_message(CHAT_ID, message)
    return jsonify({"status": "success"}), 200

# --- 3. Проверка статуса (для Render) ---
@app.route('/', methods=['GET'])
def health_check():
    return "Бот работает и ждет сигналы!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
