import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")
signals = []
entry_price = None
in_position = False

tp_ratio = 0.02  # 2% سود هدف
sl_ratio = 0.01  # 1% حد ضرر

for i in range(1, len(df)):
    ema_9_prev, ema_21_prev = df['ema_9'].iloc[i-1], df['ema_21'].iloc[i-1]
    ema_9, ema_21 = df['ema_9'].iloc[i], df['ema_21'].iloc[i]
    macd = df['macd'].iloc[i]
    macd_signal = df['macd_signal'].iloc[i]
    adx = df['adx'].iloc[i]
    close = df['close'].iloc[i]
    bb_mid = df['bb_mid'].iloc[i]

    if not in_position:
        if (ema_9_prev < ema_21_prev) and (ema_9 > ema_21) and (macd > macd_signal) and (adx > 20) and (close > bb_mid):
            signals.append("buy")
            entry_price = close
            in_position = True
        else:
            signals.append("hold")
    else:
        tp_price = entry_price * (1 + tp_ratio)
        sl_price = entry_price * (1 - sl_ratio)

        if close >= tp_price:
            signals.append("sell")  # Take Profit
            in_position = False
        elif close <= sl_price:
            signals.append("sell")  # Stop Loss
            in_position = False
        elif ema_9 < ema_21:
            signals.append("sell")  # EMA برگشت
            in_position = False
        else:
            signals.append("hold")

df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
