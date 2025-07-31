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
TP_RATIO = 0.03     # سود هدف (استفاده نمی‌کنیم چون Trailing داریم)
SL_RATIO = 0.015    # حد ضرر ثابت اولیه (۱.۵٪)
TRAIL_START = 0.015 # آغاز trailing بعد از ۱.۵٪ سود
TRAIL_OFFSET = 0.01 # استاپ دنبال‌کننده با فاصله ۱٪

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    # اندیکاتورها
    ema_9_prev = prev['ema_9']
    ema_21_prev = prev['ema_21']
    ema_9 = curr['ema_9']
    ema_21 = curr['ema_21']
    ema_200 = curr['ema_200']
    macd = curr['macd']
    macd_signal = curr['macd_signal']
    rsi = curr['rsi_14']
    close = curr['close']

    # --- ورود ---
    if not in_position:
        if (
            ema_9_prev < ema_21_prev and ema_9 > ema_21 and
            macd > macd_signal and
            30 < rsi < 75 and
            close > ema_200
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
        sl_price = entry_price * (1 - SL_RATIO)

        # اگر قیمت از SL اولیه پایین‌تر رفت
        if close <= sl_price:
            signals.append("sell")
            in_position = False
            continue

        # اگر trailing stop فعال بشه
        if (highest_price - entry_price) / entry_price >= TRAIL_START:
            trail_stop = highest_price * (1 - TRAIL_OFFSET)
            if close <= trail_stop:
                signals.append("sell")
                in_position = False
                continue

        # شرایط خروج ترکیبی: EMA + MACD + RSI
        if (
            ema_9 < ema_21 or
            macd < macd_signal or
            rsi < 30
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌های نسخه هوشمند با Trailing Stop ساخته شد.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
