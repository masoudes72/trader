import pandas as pd
import numpy as np

df = pd.read_csv("btc_15m_with_indicators.csv")

# پارامترها
POSITION_DOLLAR = 100
SL_PCT = 0.05
TP_PCT = 0.10

signals = []
entry_prices = []
exit_prices = []
position_sizes = []

in_position = False
entry_price = 0.0
position_size = 0
stop_price = 0.0
tp_price = 0.0

for i in range(1, len(df)):
    curr = df.iloc[i]
    price = curr['close']

    if not in_position:
        if price > curr['open']:
            entry_price = price
            stop_price = entry_price * (1 - SL_PCT)
            tp_price = entry_price * (1 + TP_PCT)
            position_size = POSITION_DOLLAR / entry_price

            in_position = True
            signals.append("buy")
            entry_prices.append(entry_price)
            exit_prices.append(0)
            position_sizes.append(round(position_size, 4))
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)
    else:
        if price <= stop_price:
            signals.append("sell")
            in_position = False
            exit_prices.append(stop_price)
            entry_prices.append(0)
            position_sizes.append(0)
        elif price >= tp_price:
            signals.append("sell")
            in_position = False
            exit_prices.append(tp_price)
            entry_prices.append(0)
            position_sizes.append(0)
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# خروجی
df = df.iloc[1:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌ها با exit_price دقیق ذخیره شدند.")
