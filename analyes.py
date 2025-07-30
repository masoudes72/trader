import os
import pandas as pd

try:
    # بررسی وجود فایل
    if not os.path.exists("kucoin_BTC_USDT_15m.csv"):
        raise FileNotFoundError("فایل 'mexc_BTC_USDT_15m.csv' یافت نشد.")

    # خواندن داده
    df = pd.read_csv("kucoin_BTC_USDT_15m.csv")

    # بررسی ستون‌های ضروری
    if not {'close'}.issubset(df.columns.str.lower()):
        raise ValueError("ستون 'close' در فایل یافت نشد.")

    df.columns = df.columns.str.lower()  # یکنواخت‌سازی نام ستون‌ها

    # سعی در استفاده از pandas_ta
    try:
        import pandas_ta as ta
        df['ema_9'] = ta.ema(df['close'], length=9)
        df['ema_21'] = ta.ema(df['close'], length=21)
        df['rsi_14'] = ta.rsi(df['close'], length=14)
    except ImportError:
        # محاسبه‌ی دستی EMA
        def ema(series, span):
            return series.ewm(span=span, adjust=False).mean()

        # محاسبه‌ی دستی RSI
        def rsi(series, period=14):
            delta = series.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        df['ema_9'] = ema(df['close'], 9)
        df['ema_21'] = ema(df['close'], 21)
        df['rsi_14'] = rsi(df['close'], 14)

    # نمایش ۵ ردیف اول
    print(df[['close', 'ema_9', 'ema_21', 'rsi_14']].head())

    # ذخیره خروجی
    df.to_csv("btc_15m_with_indicators.csv", index=False)
    print("فایل خروجی با موفقیت ذخیره شد: btc_15m_with_indicators.csv")

except FileNotFoundError as e:
    print(f"خطا: {e}")
except pd.errors.ParserError:
    print("خطا در خواندن فایل CSV. لطفاً فرمت فایل را بررسی کنید.")
except Exception as e:
    print(f"خطای پیش‌بینی‌نشده: {e}")

# محاسبه MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()

df['macd'] = exp1 - exp2
df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()

df.to_csv("btc_15m_with_indicators.csv", index=False)

# MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# ADX
import pandas_ta as ta
adx = ta.adx(df['high'], df['low'], df['close'], length=14)
df['adx'] = adx['ADX_14']

# Bollinger Bands
df['bb_mid'] = df['close'].rolling(window=20).mean()
df['bb_std'] = df['close'].rolling(window=20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

