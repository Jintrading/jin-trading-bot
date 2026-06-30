import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Получаем переменные окружения (настрой их в Render в разделе Environment)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(text):
    """Функция для отправки сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

@app.route('/webhook', methods=['POST'])
def handle_tradingview_webhook():
    """Единственная функция для обработки всех алертов"""
    try:
        data = request.json
        # TradingView может присылать JSON, например: {"message": "BUY LONG"}
        message = data.get('message', 'Получен сигнал без описания')
        
        print(f"Пришел сигнал: {message}")
        
        # Отправляем в Telegram
        send_telegram_message(f"🔔 <b>Сигнал TradingView:</b>\n\n{message}")
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Ошибка обработки webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Этот путь нужен для UptimeRobot, чтобы сервер не засыпал"""
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
