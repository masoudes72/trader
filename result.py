import pandas as pd
import numpy as np

# --- بارگذاری داده ---
df = pd.read_csv("btc_15m_with_indicators.csv")

# --- پارامترهای اصلی ---
POSITION_DOLLAR = 100
SL_PCT = 0.05   # حد ضرر ۵٪
TP_PCT = 0.10   # حد سود ۱۰٪

signals = []
entry_prices = []
position_sizes = []

in_position = False
entry_price = 0.0
position_size = 0
stop_price = 0.0
tp_price = 0.0

for i in range(1, len(df)):
    curr = df.iloc[i]
    price = curr['close']

    # --- ورود فقط بر اساس کندل صعودی ---
    if not in_position:
        if price > curr['open']:
            entry_price = price
            stop_price = entry_price * (1 - SL_PCT)
            tp_price = entry_price * (1 + TP_PCT)
            position_size = POSITION_DOLLAR / entry_price

            in_position = True
            signals.append("buy")
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size, 4))
        else:
            signals.append("hold")
            entry_prices.append(0)
            position_sizes.append(0)

    # --- خروج: یا به حد سود یا ضرر رسیده باشیم
    else:
        if price <= stop_price or price >= tp_price:
            signals.append("sell")
            in_position = False
            entry_price = 0
            position_size = 0
            entry_prices.append(0)
            position_sizes.append(0)
        else:
            signals.append("hold")
            entry_prices.append(0)
            position_sizes.append(0)

# --- خروجی نهایی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ استراتژی ساده با ورود بر اساس کندل صعودی، SL=5٪ و TP=10٪ تولید شد.")
