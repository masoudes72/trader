import pandas as pd
import numpy as np

# --- بارگذاری داده نهایی ---
df = pd.read_csv("btc_15m_with_indicators.csv")

# --- پارامترها ---
FIXED_POSITION_DOLLAR = 100
SL_LIMIT = 0.01  # حد ضرر: ۱٪
RR = 3
TP_LIMIT = SL_LIMIT * RR

signals = []
position_sizes = []
entry_prices = []

in_position = False
entry_price = 0.0
target_price = 0.0
stop_price = 0.0

# --- الگوهای کندلی (همون قبلی) ---
def is_bullish_engulfing(prev, curr):
    return (prev['close'] < prev['open'] and
            curr['close'] > curr['open'] and
            curr['close'] > prev['open'] and
            curr['open'] < prev['close'])

def is_hammer(curr):
    body = abs(curr['close'] - curr['open'])
    return body < (curr['high'] - curr['low']) * 0.3 and (curr['low'] < curr['open'] and curr['low'] < curr['close'])

def is_doji(curr):
    return abs(curr['close'] - curr['open']) <= (curr['high'] - curr['low']) * 0.1

# --- حلقه اصلی ---
for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    ema_9      = curr['ema_9']
    ema_21     = curr['ema_21']
    ema_200_1h = curr.get('ema_200_1h', np.nan)
    adx_1h     = curr.get('adx_1h', np.nan)
    rsi        = curr['rsi_14']
    close      = curr['close']

    candle_ok = (
        is_bullish_engulfing(prev, curr) or
        is_hammer(curr) or
        (is_doji(curr) and rsi < 30)
    )

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
            adx_1h > 25 and
            25 < rsi < 70 and
            candle_ok
        ):
            entry_price = close
            stop_price = entry_price * (1 - SL_LIMIT)
            target_price = entry_price * (1 + TP_LIMIT)

            position_size = FIXED_POSITION_DOLLAR / entry_price

            in_position = True
            signals.append("buy")
            position_sizes.append(round(position_size, 4))
            entry_prices.append(round(entry_price, 2))
        else:
            signals.append("hold")
            position_sizes.append(0)
            entry_prices.append(0)

    # --- خروج
    else:
        if close <= stop_price or close >= target_price:
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

print("✅ سیگنال‌ها با حجم ثابت 100 دلار و RR=3 تولید شدند.")
