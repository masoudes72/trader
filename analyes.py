import pandas as pd
import pandas_ta as ta
import os

# نام فایل ورودی
raw_filename = "btc_15m_raw.csv"

# بررسی وجود فایل
if not os.path.exists(raw_filename):
    raise FileNotFoundError("❌ فایل کندل ورودی (btc_15m_raw.csv) یافت نشد. لطفاً مرحله '📥 دریافت داده' را اجرا کنید.")

# بارگذاری داده‌ها
df = pd.read_csv(raw_filename)

# --- اندیکاتورهای پایه ---
df['ema_9'] = ta.ema(df['close'], length=9)
df['ema_21'] = ta.ema(df['close'], length=21)
df['rsi_14'] = ta.rsi(df['close'], length=14)
macd = ta.macd(df['close'])
df['macd'] = macd['MACD_12_26_9']
df['macd_signal'] = macd['MACDs_12_26_9']
bb = ta.bbands(df['close'], length=20)
df['bb_upper'] = bb['BBU_20_2.0']
df['bb_mid'] = bb['BBM_20_2.0']
df['bb_lower'] = bb['BBL_20_2.0']
df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
df['momentum'] = ta.mom(df['close'], length=4)
df['adx'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']

# --- اندیکاتورهای پیشرفته ---
df['stochrsi'] = ta.stochrsi(df['close'])['STOCHRSIk_14_14_3_3']
df['cci'] = ta.cci(df['high'], df['low'], df['close'], length=20)
df['williams'] = ta.willr(df['high'], df['low'], df['close'], length=14)
df['obv'] = ta.obv(df['close'], df['volume'])
df['supertrend'] = ta.supertrend(df['high'], df['low'], df['close'])['SUPERT_7_3.0']

# ذخیره خروجی
indicator_output = "btc_15m_with_indicators.csv"
df.to_csv(indicator_output, index=False)

print(f"✅ اندیکاتورها ذخیره شدند: {indicator_output}")
