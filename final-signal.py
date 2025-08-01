import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

# پارامترهای پایه
POSITION_DOLLAR = 100

signals = []
entry_prices = []
exit_prices = []
position_sizes = []

in_position = False
entry_price = 0.0
position_size = 0.0

for i in range(2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    price = curr['close']

    bias_up = curr['close'] > curr['ema_200_1h']
    bos_simple = curr['high'] > prev['high']

    # ورود فقط با bias صعودی و BOS ساده
    if not in_position:
        if bias_up and bos_simple:
            entry_price = price
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

    # خروج فقط با BOS نزولی
    else:
        bos_down = curr['low'] < prev['low']
        if bos_down:
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(0)
            position_sizes.append(0)
            in_position = False
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# ذخیره خروجی
df = df.iloc[2:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ نسخه ساده‌شده SMC فقط با BOS و bias تولید شد.")
