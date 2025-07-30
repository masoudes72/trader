import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

signals = []
in_position = False

for i in range(1, len(df)):
    ema_9 = df['ema_9'].iloc[i]
    ema_21 = df['ema_21'].iloc[i]
    macd = df['macd'].iloc[i]
    signal_line = df['signal_line'].iloc[i]
    rsi = df['rsi_14'].iloc[i]

    if not in_position and (ema_9 > ema_21 and macd > signal_line and 40 < rsi < 60):
        signals.append("buy")
        in_position = True

    elif in_position and (ema_9 < ema_21 or macd < signal_line):
        signals.append("sell")
        in_position = False

    else:
        signals.append("hold")

df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("تعداد سیگنال‌ها:")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
