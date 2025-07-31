import pandas as pd
import numpy as np
import os

# --- فایل ورودی ---
input_file = "btc_15m_raw.csv"
if not os.path.exists(input_file):
    raise FileNotFoundError("❌ فایل کندل ورودی (btc_15m_raw.csv) یافت نشد.")

df = pd.read_csv(input_file)

# --- EMA ---
df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

# --- RSI ---
delta = df['close'].diff()
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)
avg_gain = pd.Series(gain).rolling(window=14).mean()
avg_loss = pd.Series(loss).rolling(window=14).mean()
rs = avg_gain / avg_loss
df['rsi_14'] = 100 - (100 / (1 + rs))

# --- MACD ---
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = ema12 - ema26
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# --- Bollinger Bands ---
df['bb_mid'] = df['close'].rolling(window=20).mean()
df['bb_std'] = df['close'].rolling(window=20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

# --- ATR ---
high_low = df['high'] - df['low']
high_close = np.abs(df['high'] - df['close'].shift(1))
low_close = np.abs(df['low'] - df['close'].shift(1))
tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=14).mean()

# --- Momentum ---
df['momentum'] = df['close'] - df['close'].shift(4)

# --- ADX (ثابت فرض شده برای تست) ---
df['adx'] = 25

# --- ذخیره خروجی ---
df.to_csv("btc_15m_with_indicators.csv", index=False)
print("✅ اندیکاتورهای کلاسیک بدون pandas_ta محاسبه شدند.")
