import pandas as pd
import numpy as np

# --- بارگذاری داده‌ها ---
df = pd.read_csv("btc_15m_with_indicators.csv")

signals = []
in_position = False
entry_price = 0.0

# پارامترهای مدیریت ریسک
TP_RATIO = 0.03   # سود هدف: ۳٪
SL_RATIO = 0.01   # حد ضرر: ۱٪

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    # اندیکاتورها
    ema_9 = curr['ema_9']
    ema_21 = curr['ema_21']
    adx = curr['adx']
    rsi = curr['rsi_14']
    close = curr['close']

    # --- ورود (Buy) ---
    if not in_position:
        if (
            ema_9 > ema_21 and       # روند صعودی واضح
            adx > 25 and             # قدرت کافی روند
            25 < rsi < 70            # نه اشباع خرید و نه فروش
        ):
            signals.append("buy")
            in_position = True
            entry_price = close
        else:
            signals.append("hold")

    # --- خروج (Sell) ---
    else:
        tp_price = entry_price * (1 + TP_RATIO)
        sl_price = entry_price * (1 - SL_RATIO)

        if (
            close >= tp_price or     # رسیدن به تارگت سود
            close <= sl_price or     # رسیدن به حد ضرر
            ema_9 < ema_21 or        # کراس نزولی EMA
            rsi >= 75 or rsi <= 25   # ورود به نواحی اشباع شدید
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌های نسخه بهینه‌شده (EMA + ADX + RSI) تولید شدند.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
