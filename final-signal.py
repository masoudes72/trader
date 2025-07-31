import pandas as pd
import numpy as np

# --- بارگذاری داده ---
df = pd.read_csv("btc_15m_with_indicators.csv")
signals = []

# وضعیت معامله
in_position = False
entry_price = 0.0
highest_price = 0.0

# پارامترها
TRAIL_START = 0.015     # شروع trailing بعد از 1.5٪ سود
TRAIL_GAP   = 0.01       # فاصله trailing = 1٪
SL_LIMIT    = 0.015      # حد ضرر اضطراری (درصورت ریزش شدید)

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    # اندیکاتورها
    ema_9  = curr['ema_9']
    ema_21 = curr['ema_21']
    adx    = curr['adx']
    rsi    = curr['rsi_14']
    close  = curr['close']

    # --- ورود ---
    if not in_position:
        if (
            ema_9 > ema_21 and
            adx > 25 and
            25 < rsi < 70
        ):
            signals.append("buy")
            in_position = True
            entry_price = close
            highest_price = close
        else:
            signals.append("hold")

    # --- خروج ---
    else:
        highest_price = max(highest_price, close)
        stop_price = entry_price * (1 - SL_LIMIT)

        # ❗ خروج فوری در صورت ضرر بزرگ
        if close <= stop_price:
            signals.append("sell")
            in_position = False
            continue

        # ✅ Trailing Stop فعال شد؟
        if (highest_price - entry_price) / entry_price >= TRAIL_START:
            trail_stop = highest_price * (1 - TRAIL_GAP)
            if close <= trail_stop:
                signals.append("sell")
                in_position = False
                continue

        # ❗ خروج در شرایط ضعف (EMA کراس یا RSI اشباع)
        if (
            ema_9 < ema_21 or
            rsi >= 75 or
            rsi <= 25
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌های نسخه نهایی تولید شدند.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
