from flask import Flask, request
import telegram
import os

app = Flask(__name__)

# ================== НАСТРОЙКИ ==================
TOKEN = "8918083070:AAE_fWUOO_5X_lly7K3pFIaLaxiVHtlyh1M" 
CHAT_ID = "318740554"           
# ===============================================

bot = telegram.Bot(token=TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            message = data['message']
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
            return "OK", 200
    except Exception as e:
        print("Error:", e)
    return "ERROR", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
// ======================
// ФИЛЬТР АКТИВОВ — ТОЛЬКО ВЫБРАННЫЕ
// ======================
allowed = array.from("BTCUSDT", "ETHUSDT", "ADAUSDT", "XRPUSDT", "XLMUSDT", 
                     "ALGOUSDT", "OPUSDT", "RNDRUSDT", "ICPUSDT", "APEUSDT", 
                     "HAGUSDT", "TSLA", "TAO", "LINKUSDT", "GOLD")

isAllowed = false
for i = 0 to array.size(allowed) - 1
    if str.contains(syminfo.ticker, array.get(allowed, i))
        isAllowed := true

// ======================
// СИГНАЛ ТОЛЬКО ПО РАЗРЕШЁННЫМ АКТИВАМ
// ======================
if (buySignal or sellSignal) and isAllowed and barstate.islast
    direction = buySignal ? "Long (L)" : "Short (S)"
    certainty = buySignal ? math.round(buyPower) : math.round(sellPower)
    
    signalText = "🚀 **Jin Trading Signal**\n\n" +
                 "Pair: **" + syminfo.ticker + "**\n" +
                 "Direction: **" + direction + "**\n" +
                 "Certainty: **" + str.tostring(certainty) + "%**\n" +
                 "Entry: **" + str.tostring(close, "#.##") + "**\n\n" +
                 "🤖 **Торгуй здесь:** [Jin Trading Bot](https://t.me/Jin_tradingbot)"

    alert(signalText, alert.freq_once_per_bar_close)