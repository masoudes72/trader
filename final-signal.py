import pandas as pd
import numpy as np

# --- بارگذاری دیتاست ---
df = pd.read_csv("btc_15m_with_indicators.csv")

signals = []
in_position = False
entry_price = 0.0

# --- پارامترهای استراتژی ---
TP_RATIO = 0.03    # تارگت سود: ۳٪
SL_RATIO = 0.015   # حد ضرر: ۱.۵٪

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    # --- اندیکاتورها ---
    ema_9_prev = prev['ema_9']
    ema_21_prev = prev['ema_21']
    ema_9 = curr['ema_9']
    ema_21 = curr['ema_21']
    macd = curr['macd']
    macd_signal = curr['macd_signal']
    rsi = curr['rsi_14']
    obv_diff = curr['obv'] - prev['obv']
    adx = curr['adx']
    close = curr['close']
    bb_mid = curr['bb_mid']

    # --- ورود ---
    if not in_position:
        if (
            ema_9_prev < ema_21_prev and ema_9 > ema_21 and
            macd > macd_signal and macd > 0 and
            40 < rsi < 70 and
            obv_diff > 0 and
            adx > 20 and
            close > bb_mid
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
            macd < macd_signal or
            rsi > 75 or rsi < 30
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

# --- خلاصه آماری ---
print("✅ سیگنال‌ها تولید شدند.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
