import pandas as pd
import numpy as np

# --- بارگذاری داده‌ها ---
df = pd.read_csv("btc_15m_with_indicators.csv")
df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

signals = []
in_position = False
entry_price = 0.0
highest_price = 0.0

# پارامترها
TRAIL_START = 0.012     # آغاز trailing از 1.2٪ سود
TRAIL_GAP   = 0.008      # فاصله trailing = 0.8٪
SL_LIMIT    = 0.01       # حد ضرر اضطراری 1٪

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    ema_9     = curr['ema_9']
    ema_21    = curr['ema_21']
    ema_200   = curr['ema_200']
    adx       = curr['adx']
    rsi       = curr['rsi_14']
    close     = curr['close']

    # ⛔ اگر ADX خیلی پایین بود، هیچ کاری نکن
    if adx < 20:
        signals.append("hold")
        continue

    # --- ورود ---
    if not in_position:
        if (
            ema_9 > ema_21 and
            close > ema_200 and
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
        sl_price = entry_price * (1 - SL_LIMIT)

        # ❗ حد ضرر اضطراری
        if close <= sl_price:
            signals.append("sell")
            in_position = False
            continue

        # ✅ Trailing Stop
        if (highest_price - entry_price) / entry_price >= TRAIL_START:
            trail_stop = highest_price * (1 - TRAIL_GAP)
            if close <= trail_stop:
                signals.append("sell")
                in_position = False
                continue

        # ❗ خروج در اشباع یا تضعیف
        if (
            ema_9 < ema_21 or
            rsi >= 75 or
            rsi <= 25
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ نسخه نهایی با فیلتر روند و خروج هوشمند تولید شد.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
