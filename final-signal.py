import pandas as pd
import numpy as np

# --- بارگذاری داده ---
df = pd.read_csv("btc_15m_with_indicators.csv")
df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

# --- پارامترها ---
initial_balance = 10000
risk_per_trade = 0.02  # ریسک ۲٪
SL_LIMIT = 0.01        # حد ضرر ۱٪ پایین‌تر
TRAIL_START = 0.012
TRAIL_GAP = 0.008

# --- سیگنال‌سازی ---
signals = []
position_sizes = []
entry_prices = []

in_position = False
entry_price = 0.0
highest_price = 0.0
balance = initial_balance

# --- تشخیص الگوهای کندلی ---
def is_bullish_engulfing(prev, curr):
    return (prev['close'] < prev['open'] and
            curr['close'] > curr['open'] and
            curr['close'] > prev['open'] and
            curr['open'] < prev['close'])

def is_hammer(curr):
    body = abs(curr['close'] - curr['open'])
    lower_shadow = curr['open'] - curr['low'] if curr['open'] < curr['close'] else curr['close'] - curr['low']
    upper_shadow = curr['high'] - curr['close'] if curr['close'] > curr['open'] else curr['high'] - curr['open']
    return lower_shadow > 2 * body and upper_shadow < body

def is_doji(curr):
    return abs(curr['close'] - curr['open']) <= (curr['high'] - curr['low']) * 0.1

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    ema_9 = curr['ema_9']
    ema_21 = curr['ema_21']
    ema_200 = curr['ema_200']
    adx = curr['adx']
    rsi = curr['rsi_14']
    close = curr['close']

    candle_engulfing = is_bullish_engulfing(prev, curr)
    candle_hammer = is_hammer(curr)
    candle_doji_rsi = is_doji(curr) and rsi < 30

    if adx < 20:
        signals.append("hold")
        position_sizes.append(0)
        entry_prices.append(0)
        continue

    # --- ورود ---
    if not in_position:
        if (
            ema_9 > ema_21 and
            close > ema_200 and
            adx > 25 and
            25 < rsi < 70 and
            (candle_engulfing or candle_hammer or candle_doji_rsi)
        ):
            # محاسبه حد ضرر و اندازه پوزیشن
            sl_price = close * (1 - SL_LIMIT)
            stop_size = close - sl_price
            position_size = (balance * risk_per_trade) / stop_size
            position_size = min(position_size, balance)  # نمی‌تونه بیشتر از موجودی باشه

            signals.append("buy")
            in_position = True
            entry_price = close
            highest_price = close
            position_sizes.append(round(position_size, 2))
            entry_prices.append(round(entry_price, 2))
        else:
            signals.append("hold")
            position_sizes.append(0)
            entry_prices.append(0)

    # --- خروج ---
    else:
        highest_price = max(highest_price, close)
        sl_price = entry_price * (1 - SL_LIMIT)

        if close <= sl_price:
            signals.append("sell")
            in_position = False
            position_sizes.append(0)
            entry_prices.append(0)
            continue

        if (highest_price - entry_price) / entry_price >= TRAIL_START:
            trail_stop = highest_price * (1 - TRAIL_GAP)
            if close <= trail_stop:
                signals.append("sell")
                in_position = False
                position_sizes.append(0)
                entry_prices.append(0)
                continue

        if (
            ema_9 < ema_21 or
            rsi >= 75 or
            rsi <= 25
        ):
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

        position_sizes.append(0)
        entry_prices.append(0)

# --- خروجی نهایی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ استراتژی ترکیبی الگوی کندلی + Position Sizing اجرا شد.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
