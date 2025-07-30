import pandas as pd
import os

# استفاده از فایل با نام مشخص
raw_filename = "btc_15m_raw.csv"

# بررسی وجود فایل داده خام
if not os.path.exists(raw_filename):
    raise FileNotFoundError("❌ فایل کندل ورودی (btc_15m_raw.csv) یافت نشد. لطفاً مرحله '📥 دریافت داده' را اجرا کنید.")

# بارگذاری داده‌ها
df = pd.read_csv(raw_filename)

# EMA
df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

# RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df['rsi_14'] = 100 - (100 / (1 + rs))

# MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# Bollinger Bands
df['bb_mid'] = df['close'].rolling(window=20).mean()
df['bb_std'] = df['close'].rolling(window=20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

# ATR
df['H-L'] = df['high'] - df['low']
df['H-PC'] = abs(df['high'] - df['close'].shift(1))
df['L-PC'] = abs(df['low'] - df['close'].shift(1))
df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
df['atr'] = df['TR'].rolling(window=14).mean()

# Momentum
df['momentum'] = df['close'] - df['close'].shift(4)

# ADX ثابت
df['adx'] = 25

# ذخیره خروجی نهایی
indicator_output = "btc_15m_with_indicators.csv"
df.to_csv(indicator_output, index=False)
print(f"✅ اندیکاتورها ذخیره شدند: {indicator_output}")
