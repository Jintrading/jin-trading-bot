from flask import Flask, request
import telegram
import os
import asyncio

app = Flask(__name__)

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

bot = telegram.Bot(token=TOKEN)

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

# ================== ТЕСТОВЫЕ КОМАНДЫ ==================
@app.route('/start', methods=['GET'])
def start():
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text="🚀 Jin Trading Bot онлайн!"))
    return "Start message sent!"

@app.route('/analyze', methods=['GET'])
def analyze():
    symbol = request.args.get('symbol', 'BTC')
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"🔍 Анализ {symbol}USDT запущен..."))
    return f"Analyze {symbol} sent"

@app.route('/status', methods=['GET'])
def status():
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text="✅ Бот работает\n🌐 Webhook активен"))
    return "Status OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Jin Trading Bot запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)