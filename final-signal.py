import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

# ⚙️ پارامترها
POSITION_DOLLAR = 100
MIN_BOS_PCT = 0.005         # حداقل قدرت BOS برای ورود = 0.5٪
TP1_PCT = 0.05              # حد سود جزئی (partial TP) در 5٪
TP2_PCT = 0.06              # حد سود کامل در 6٪
BREAKEVEN_TRIGGER = 0.03    # breakeven بعد از 3٪

# متغیرهای خروجی
signals = []
entry_prices = []
exit_prices = []
position_sizes = []

# وضعیت
in_position = False
entry_price = 0.0
position_size = 0.0
partial_tp_taken = False
breakeven_activated = False

for i in range(2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    price = curr['close']

    bias_up = curr['close'] > curr['ema_200_1h']
    bos_simple = curr['high'] > prev['high']
    bos_strength = (curr['high'] - prev['high']) / prev['high'] if prev['high'] > 0 else 0

    # ورود
    if not in_position:
        if bias_up and bos_simple and bos_strength >= MIN_BOS_PCT:
            entry_price = price
            position_size = POSITION_DOLLAR / entry_price
            in_position = True
            partial_tp_taken = False
            breakeven_activated = False

            signals.append("buy")
            entry_prices.append(entry_price)
            exit_prices.append(0)
            position_sizes.append(round(position_size, 4))
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

    # خروج
    else:
        gain = (price - entry_price) / entry_price

        if gain >= TP1_PCT and not partial_tp_taken:
            # خروج نیمه اول در partial TP
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size / 2, 4))
            partial_tp_taken = True

        elif gain >= TP2_PCT:
            # full TP برای نیمه باقی‌مانده
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size if not partial_tp_taken else position_size / 2, 4))
            in_position = False

        elif gain >= BREAKEVEN_TRIGGER:
            breakeven_activated = True
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

        elif price <= entry_price and breakeven_activated:
            # خروج breakeven برای نیمه باقی‌مانده
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size / 2 if partial_tp_taken else position_size, 4))
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

print("✅ نسخه final-signal.py با partial TP (5٪)، full TP (6٪) و breakeven (3٪) ذخیره شد.")
