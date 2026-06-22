from flask import Flask, request
import os
from telegram import Bot

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = 318740554

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    symbol = data.get('symbol', 'UNKNOWN')
    signal = data.get('signal', 'UNKNOWN')
    price = data.get('price', 0)

    message = f"🚨 {symbol} — {signal}\nЦена: {price}"
    Bot(TOKEN).send_message(chat_id=CHAT_ID, text=message)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
