from flask import Flask, request
import os
from telegram import Bot

TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M"
CHAT_ID = 318740554

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'UNKNOWN')
        signal = data.get('signal', 'UNKNOWN')
        price = data.get('price', 0)
        power = data.get('power', 0)

        message = f"🚨 {symbol} — {signal}\nЦена: {price}\nСила: {power}%"
        Bot(TOKEN).send_message(chat_id=CHAT_ID, text=message)
        return "OK", 200
    except Exception as e:
        print("Error:", e)
        return "Error", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
