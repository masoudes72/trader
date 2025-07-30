import ccxt
import pandas as pd
import time

# پارامترها
symbol = 'BTC/USDT'
timeframe = '15m'
limit = 1000
exchange = ccxt.kucoin()

# دریافت اطلاعات
print("🚀 شروع دریافت اطلاعات از Kucoin...")
print(f"📡 در حال درخواست {limit} کندل برای {symbol}...")

data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

# ساخت دیتافریم
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# ذخیره با نام ثابت
filename = "btc_15m_raw.csv"
df.to_csv(filename, index=False)

print(f"📁 ذخیره شد در فایل: {filename}")
