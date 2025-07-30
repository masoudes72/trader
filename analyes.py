import pandas as pd
import os

# پیدا کردن فایل CSV معتبر (مثلاً kucoin_BTC_USDT_15m.csv)
for file in os.listdir():
    if file.endswith("_BTC_USDT_15m.csv"):
        df = pd.read_csv(file)
        break
else:
    raise FileNotFoundError("فایل دیتای کندل یافت نشد.")

# محاسبه EMA
df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()

# محاسبه RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
df['rsi_14'] = 100 - (100 / (1 + rs))

# محاسبه MACD و MACD Signal
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# Bollinger Bands
df['bb_mid'] = df['close'].rolling(window=20).mean()
df['bb_std'] = df['close'].rolling(window=20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

# مقدار ثابت ADX برای تست
df['adx'] = 25

# ذخیره خروجی
df.to_csv("btc_15m_with_indicators.csv", index=False)
print("✅ اندیکاتورها محاسبه و ذخیره شدند.")
