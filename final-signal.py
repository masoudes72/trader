import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

# ⚙️ پارامترها
POSITION_DOLLAR = 100                 # حجم معامله ثابت
MIN_BOS_PCT = 0.005                   # حداقل قدرت BOS (0.5٪)
TP_PCT = 0.10                         # حد سود کامل 10٪
BREAKEVEN_TRIGGER = 0.03             # فعال‌سازی breakeven در 3٪ سود

# 📦 متغیرهای خروجی
signals = []
entry_prices = []
exit_prices = []
position_sizes = []

# 🎯 متغیرهای وضعیت
in_position = False
entry_price = 0.0
position_size = 0.0
breakeven_activated = False

for i in range(2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    price = curr['close']

    # 📈 شرایط ورود
    bias_up = curr['close'] > curr['ema_200_1h']
    bos_simple = curr['high'] > prev['high']
    bos_strength = (curr['high'] - prev['high']) / prev['high'] if prev['high'] > 0 else 0

    if not in_position:
        if bias_up and bos_simple and bos_strength >= MIN_BOS_PCT:
            entry_price = price
            position_size = POSITION_DOLLAR / entry_price
            in_position = True
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

    else:
        # 📉 شرایط خروج
        gain = (price - entry_price) / entry_price
        if gain >= BREAKEVEN_TRIGGER:
            breakeven_activated = True

        bos_down = curr['low'] < prev['low']
        full_tp = gain >= TP_PCT
        return_to_entry = price <= entry_price and breakeven_activated

        if bos_down or return_to_entry or full_tp:
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(entry_price)
            position_sizes.append(round(position_size, 4))
            in_position = False
            entry_price = 0
            position_size = 0
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# 💾 خروجی نهایی
df = df.iloc[2:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ فایل final-signal.py با منطق BOS قوی + breakeven + TP کامل ذخیره شد.")
