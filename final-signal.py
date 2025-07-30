import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

signals = []

for i in range(1, len(df)):
    ema_9_prev, ema_21_prev = df['ema_9'].iloc[i-1], df['ema_21'].iloc[i-1]
    ema_9, ema_21 = df['ema_9'].iloc[i], df['ema_21'].iloc[i]
    macd, signal_line = df['macd'].iloc[i], df['signal_line'].iloc[i]
    rsi = df['rsi_14'].iloc[i]

    # ورود به معامله
    if (ema_9_prev < ema_21_prev) and (ema_9 > ema_21) and (macd > signal_line) and (rsi < 65):
        signals.append("buy")

    # خروج از معامله
    elif (ema_9_prev > ema_21_prev) and (ema_9 < ema_21) and (macd < signal_line) and (rsi > 35):
        signals.append("sell")

    else:
        signals.append("hold")

df = df.iloc[1:].copy()
df['signal'] = signals

df.to_csv("btc_signals_15m.csv", index=False)

print("تعداد سیگنال‌ها:")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
