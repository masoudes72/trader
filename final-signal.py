import pandas as pd
import numpy as np

# --- بارگذاری داده‌ها ---
df = pd.read_csv("btc_15m_with_indicators.csv")

# محاسبه EMA200 برای فیلتر روند کلی
df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

signals = []
in_position = False
entry_price = 0.0

TP_RATIO = 0.03    # هدف سود ۳٪
SL_RATIO = 0.015   # حد ضرر ۱.۵٪

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
            ema_9_prev < ema_21_prev and ema_9 > ema_21 and  # کراس صعودی EMA
            macd > macd_signal and                           # مومنتوم مثبت
            30 < rsi < 75 and                                # RSI در محدوده قابل قبول
            close > ema_200                                  # فیلتر روند کلی
        ):
            signals.append("buy")
            in_position = True
            entry_price = close
        else:
            signals.append("hold")

    # --- خروج ---
    else:
        tp_price = entry_price * (1 + TP_RATIO)
        sl_price = entry_price * (1 - SL_RATIO)

        if (
            close >= tp_price or
            close <= sl_price or
            ema_9 < ema_21 or
            macd < macd_signal
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌ها بر اساس نسخه بهینه‌شده تولید شدند.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
