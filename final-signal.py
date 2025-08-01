import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

POSITION_DOLLAR = 100

signals = []
entry_prices = []
exit_prices = []
position_sizes = []

in_position = False
entry_price = 0.0
position_size = 0

for i in range(2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    prev2 = df.iloc[i - 2]
    price = curr['close']

    bias_up = curr['close'] > curr['ema_200_1h']
    liquidity_sweep = curr['low'] < prev['low'] and curr['close'] > curr['open']
    bos_simple = curr['high'] > prev['high']

    # --- ورود ---
    if not in_position:
        if bias_up and liquidity_sweep and bos_simple:
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

    # --- خروج ---
    else:
        exit_condition = (
            curr['close'] < curr['open'] and
            curr['low'] < prev['low']
        )

        if exit_condition:
            signals.append("sell")
            in_position = False
            exit_prices.append(price)
            entry_prices.append(0)
            position_sizes.append(0)
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# خروجی
df = df.iloc[2:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ منطق SMC با BOS ساده و بدون SL/TP درصدی با موفقیت پیاده‌سازی شد.")
