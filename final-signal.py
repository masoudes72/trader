import pandas as pd
import numpy as np

df = pd.read_csv("btc_15m_with_indicators.csv")

# --- پارامترهای استراتژی ---
POSITION_DOLLAR = 100
MAX_RISK_DOLLAR = 40
RR = 1.5
TRAIL_ACTIVE_AT = 1.0
TRAIL_DISTANCE = 20  # دلار

signals = []
entry_prices = []
position_sizes = []

in_position = False
entry_price = 0
position_size = 0
stop_price = 0
tp_price = 0
trailing_active = False
trailing_stop = 0

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    price = curr['close']

    # کندل ساده صعودی
    candle_ok = curr['close'] > curr['open']

    # ورود
    if not in_position:
        if (
            candle_ok and
            curr['ema_9'] > curr['ema_21'] and
            curr['close'] > curr['ema_200_1h']
        ):
            entry_price = price
            stop_price = entry_price - (MAX_RISK_DOLLAR / POSITION_DOLLAR) * entry_price
            tp_price = entry_price + RR * (entry_price - stop_price)
            position_size = POSITION_DOLLAR / entry_price

            in_position = True
            trailing_active = False
            trailing_stop = 0

            signals.append("buy")
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size, 4))
        else:
            signals.append("hold")
            entry_prices.append(0)
            position_sizes.append(0)

    # خروج
    else:
        gain = (price - entry_price) * position_size

        # فعال‌سازی trailing stop
        if not trailing_active and gain >= MAX_RISK_DOLLAR:
            trailing_active = True
            trailing_stop = price - (TRAIL_DISTANCE / position_size)

        # خروج به دلایل مختلف
        if price <= stop_price or (trailing_active and price <= trailing_stop):
            signals.append("sell")
            in_position = False
            entry_price = 0
            position_size = 0
            trailing_active = False
            entry_prices.append(0)
            position_sizes.append(0)

        elif not trailing_active and price >= tp_price:
            signals.append("sell")
            in_position = False
            entry_price = 0
            position_size = 0
            trailing_active = False
            entry_prices.append(0)
            position_sizes.append(0)

        else:
            # بروزرسانی trailing stop
            if trailing_active and price - (TRAIL_DISTANCE / position_size) > trailing_stop:
                trailing_stop = price - (TRAIL_DISTANCE / position_size)

            signals.append("hold")
            entry_prices.append(0)
            position_sizes.append(0)

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ نسخه ساده‌شده با ورود راحت‌تر، RR=1.5، ضرر ثابت 40 دلار و حجم ثابت 100 دلار تولید شد.")
