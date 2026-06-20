//@version=5
indicator("Jin Trading Wave PRO - Filtered", overlay=true, max_lines_count=500, max_labels_count=500)

// ======================
// НАСТРОЙКИ
// ======================
swingLength = input.int(90, "Swing Length")
deepLength  = input.int(280, "Deep Low Length")
greenOffset = input.float(-0.18, "Green Zone Offset", minval=-0.35, maxval=0.0, step=0.01)

// ======================
// ЗОНЫ
// ======================
deepLow   = ta.lowest(low, deepLength)
swingLow  = ta.lowest(low, swingLength)
swingHigh = ta.highest(high, swingLength)
waveSize  = swingHigh - swingLow

greenZone  = deepLow + waveSize * greenOffset
yellowZone = swingLow + waveSize * 0.236
whiteZone  = swingLow + waveSize * 0.382
orangeZone = swingLow + waveSize * 0.618
redZone    = swingHigh

// ======================
// ИНДИКАТОРЫ
// ======================
rsi = ta.rsi(close, 14)
[_, _, hist] = ta.macd(close, 12, 26, 9)
emaFast = ta.ema(close, 50)
emaSlow = ta.ema(close, 200)

trendBull = emaFast > emaSlow

// ======================
// POWER
// ======================
buyPower = 0.0
buyPower += rsi < 40 ? 35 : rsi < 50 ? 20 : 0
buyPower += hist > hist[1] and hist > 0 ? 30 : 0
buyPower += trendBull ? 25 : 0
buyPower += close <= yellowZone ? 20 : 0

sellPower = 100 - buyPower

buySignal  = buyPower >= 78
sellSignal = sellPower >= 78

// ======================
// ФИЛЬТР АКТИВОВ
// ======================
allowedAssets = array.from("BTCUSDT", "ETHUSDT", "ADAUSDT", "XRPUSDT", "XLMUSDT", 
                           "ALGOUSDT", "OPUSDT", "RNDRUSDT", "ICPUSDT", "APEUSDT", 
                           "HAGUSDT", "TSLA", "TAO", "LINKUSDT", "GOLD")

isAllowed = false
for i = 0 to array.size(allowedAssets) - 1
    if str.contains(syminfo.ticker, array.get(allowedAssets, i))
        isAllowed := true

// ======================
// СИГНАЛ + ОТПРАВКА
// ======================
if (buySignal or sellSignal) and isAllowed and barstate.islast
    direction = buySignal ? "Long (L)" : "Short (S)"
    certainty = buySignal ? math.round(buyPower) : math.round(sellPower)
    
    signalText = "🚀 **Jin Trading Signal**\n\n" +
                 "Pair: **" + syminfo.ticker + "**\n" +
                 "Direction: **" + direction + "**\n" +
                 "Certainty: **" + str.tostring(certainty) + "%**\n" +
                 "Entry: **" + str.tostring(close, "#.####") + "**\n\n" +
                 "🤖 **Торгуй здесь:** [Jin Trading Bot](https://t.me/Jin_tradingbot)"

    alert(signalText, alert.freq_once_per_bar_close)

// ======================
// ВИЗУАЛ
// ======================
plot(greenZone,  "Strong Buy",  color=color.new(color.green, 0), linewidth=3)
plot(yellowZone, "Buy Zone",    color=color.new(color.yellow,0), linewidth=2)
plot(whiteZone,  "Watch",       color=color.new(color.gray,0),   linewidth=2)
plot(orangeZone, "Exit",        color=color.new(color.orange,0), linewidth=2)
plot(redZone,    "Strong Sell", color=color.new(color.red,0),    linewidth=3)

plot(emaFast, color=color.blue, linewidth=2)
plot(emaSlow, color=color.purple, linewidth=2)

plotshape(buySignal and isAllowed,  title="BUY",  location=location.belowbar, color=color.green, style=shape.triangleup,   size=size.large, text="BUY")
plotshape(sellSignal and isAllowed, title="SELL", location=location.abovebar, color=color.red,   style=shape.triangledown, size=size.large, text="SELL")