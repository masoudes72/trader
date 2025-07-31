import pandas as pd
import numpy as np

# --- بارگذاری داده نهایی ---
df = pd.read_csv("btc_15m_with_indicators.csv")

# --- پارامترها ---
initial_balance = 10000
risk_per_trade = 0.02
SL_LIMIT = 0.01
TRAIL_START = 0.012
TRAIL_GAP = 0.008

signals = []
position_sizes = []
entry_prices = []

in_position = False
entry_price = 0.0
highest_price = 0.0
balance = initial_balance

# --- الگوهای کندلی ---
def is_bullish_engulfing(prev, curr):
    return (prev['close'] < prev['open'] and
            curr['close'] > curr['open'] and
            curr['close'] > prev['open'] and
            curr['open'] < prev['close'])

def is_hammer(curr):
    body = abs(curr['close'] - curr['open'])
    lower_shadow = curr['low']
    return body < (curr['high'] - curr['low']) * 0.3 and (curr['low'] < curr['open'] and curr['low'] < curr['close'])

def is_doji(curr):
    return abs(curr['close'] - curr['open']) <= (curr['high'] - curr['low']) * 0.1

# --- حلقه اصلی ---
for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    ema_9      = curr['ema_9']
    ema_21     = curr['ema_21']
    ema_200_1h = curr['ema_200_1h']
    adx_1h     = curr['adx_1h']
    adx        = curr['adx']
    rsi        = curr['rsi_14']
    close      = curr['close']

    # کندل تاییدی
    candle_ok = (
        is_bullish_engulfing(prev, curr) or
        is_hammer(curr) or
        (is_doji(curr) and rsi < 30)
    )

    # --- اگر روند کلان ضعیف است، ترید نکن
    if pd.isna(ema_200_1h) or pd.isna(adx_1h) or adx_1h < 20:
        signals.append("hold")
        position_sizes.append(0)
        entry_prices.append(0)
        continue

    # --- ورود
    if not in_position:
        if (
            ema_9 > ema_21 and
            close > ema_200_1h and
            adx > 25 and
            25 < rsi < 70 and
            candle_ok
        ):
            sl_price = close * (1 - SL_LIMIT)
            stop_size = close - sl_price
            position_size = (balance * risk_per_trade) / stop_size
            position_size = min(position_size, balance)

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

    # --- خروج
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

        if ema_9 < ema_21 or rsi >= 75 or rsi <= 25:
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

        position_sizes.append(0)
        entry_prices.append(0)

# --- ذخیره خروجی ---
df = df.iloc[1:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ نسخه نهایی با تحلیل چند تایم‌فریمی و فیلتر روند تولید شد.")
