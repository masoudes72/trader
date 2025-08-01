import pandas as pd

df = pd.read_csv("btc_15m_with_indicators.csv")

# --- پارامترها ---
POSITION_DOLLAR = 100
BREAKEVEN_TRIGGER = 0.03  # 3% سود برای breakeven
ATR_PERIOD = 10

# --- محاسبه ATR ساده ---
df['atr'] = df['high'] - df['low']
df['atr_avg'] = df['atr'].rolling(window=ATR_PERIOD).mean()

# --- خروجی‌ها ---
signals = []
entry_prices = []
exit_prices = []
position_sizes = []

in_position = False
entry_price = 0.0
position_size = 0
breakeven_activated = False

for i in range(ATR_PERIOD + 2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    prev2 = df.iloc[i - 2]

    price = curr['close']
    atr = curr['atr']
    atr_avg = curr['atr_avg']
    bias_up = curr['close'] > curr['ema_200_1h']

    liquidity_sweep = curr['low'] < prev['low'] and curr['close'] > curr['open']
    bos_strong = (
        curr['high'] > prev['high'] and
        curr['close'] > prev['close'] and
        prev['close'] > prev2['close']
    )
    atr_spike = atr > atr_avg
    no_range = (df['high'].iloc[i - 5:i].max() - df['low'].iloc[i - 5:i].min()) > atr_avg

    # --- ورود ---
    if not in_position:
        if bias_up and liquidity_sweep and bos_strong and atr_spike and no_range:
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

    # --- خروج ---
    else:
        exit_bos_down = curr['low'] < prev['low'] and curr['close'] < prev['close']
        reached_breakeven = (price - entry_price) / entry_price >= BREAKEVEN_TRIGGER
        return_to_entry = price <= entry_price and breakeven_activated

        if exit_bos_down or return_to_entry:
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(0)
            position_sizes.append(0)
            in_position = False
        else:
            if reached_breakeven:
                breakeven_activated = True
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# --- خروجی نهایی ---
df = df.iloc[ATR_PERIOD + 2:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ نسخه پیشرفته SMC با BOS قوی، ATR spike، مدیریت breakeven و خروج ساختاری تولید شد.")
