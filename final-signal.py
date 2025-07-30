import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

signals = []
in_position = False

for i in range(2, len(df)):
    ema_9 = df['ema_9'].iloc[i]
    ema_21 = df['ema_21'].iloc[i]
    rsi = df['rsi_14'].iloc[i]
    rsi_prev1 = df['rsi_14'].iloc[i-1]
    rsi_prev2 = df['rsi_14'].iloc[i-2]

    if not in_position:
        # ورود زمانی که RSI از حالت اشباع فروش برگشته و EMA تایید می‌دهد
        if (ema_9 > ema_21) and (rsi_prev2 < 30 and rsi_prev1 < 35 and rsi > 35):
            signals.append("buy")
            in_position = True
        else:
            signals.append("hold")
    else:
        # خروج زمانی که RSI بیش از حد رشد کرده یا روند معکوس شده
        if rsi > 70 or ema_9 < ema_21:
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# اصلاح طول DataFrame برای هم‌تراز کردن با طول سیگنال
df = df.iloc[2:].copy()
df['signal'] = signals

df.to_csv("btc_signals_15m.csv", index=False)

print("تعداد سیگنال‌ها:")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
