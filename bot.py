from flask import Flask, request
import telegram
import os
import asyncio

app = Flask(__name__)

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

bot = telegram.Bot(token=TOKEN)

# Webhook от TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            message = data['message']
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown'))
            return "OK", 200
    except:
        pass
    return "ERROR", 500

# Команды
@app.route('/start', methods=['GET'])
def start():
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text="🚀 Jin Trading Bot онлайн!\n\nИспользуй /analyze BTC"))
    return "Start OK"

@app.route('/analyze', methods=['GET'])
def analyze():
    symbol = request.args.get('symbol', 'BTC').upper()
    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=f"🔍 Анализ {symbol}USDT запущен..."))
    return "Analyze OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Bot запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)