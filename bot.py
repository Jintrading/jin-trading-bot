from flask import Flask, request
import telegram
import os
import asyncio

app = Flask(__name__)

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = "318740554"

bot = telegram.Bot(token=TOKEN, request=telegram.request.HTTPXRequest(timeout=30))

# ================== WEBHOOK ==================
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            message = data['message']
            asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', timeout=30))
            return "OK", 200
    except Exception as e:
        print("Webhook Error:", str(e))
    return "ERROR", 500

# ================== ТЕСТ ==================
@app.route('/start', methods=['GET'])
def start():
    try:
        asyncio.run(bot.send_message(chat_id=CHAT_ID, text="🚀 Jin Trading Bot онлайн!", timeout=30))
        return "Start sent!"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Bot запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)