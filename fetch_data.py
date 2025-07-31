import ccxt
import pandas as pd
import time

# --- پارامترها ---
symbol = 'BTC/USDT'
exchange = ccxt.binance()
limit = 1000

# --- تابع دریافت دیتا ---
def fetch_ohlcv(symbol, tf):
    data = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# --- دانلود داده تایم‌فریم 15m ---
print("📥 دریافت داده 15 دقیقه‌ای...")
df_15m = fetch_ohlcv(symbol, '15m')
df_15m.to_csv("btc_15m_raw.csv", index=False)
print("✅ ذخیره شد: btc_15m_raw.csv")

# --- دانلود داده تایم‌فریم 1h ---
time.sleep(1)
print("📥 دریافت داده 1 ساعته...")
df_1h = fetch_ohlcv(symbol, '1h')
df_1h.to_csv("btc_1h_raw.csv", index=False)
print("✅ ذخیره شد: btc_1h_raw.csv")
