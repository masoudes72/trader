# محتوای کامل برای فایل fetch_data.py

import ccxt
import pandas as pd
import pandas_ta as ta

# این تابع بدون تغییر باقی می‌ماند
def get_exchange():
    return ccxt.binance({
        'rateLimit': 1200,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })

# این تابع به طور کامل بازنویسی و اصلاح شده است
def fetch_data(symbol='BTC/USDT', timeframe='15m', limit=1000):
    """
    داده‌های قیمت را دریافت کرده و اندیکاتورهای لازم را محاسبه می‌کند.
    منطق محاسبه EMA یک ساعته به طور کامل اصلاح شده است.
    """
    print(f"Fetching {limit} candles for {symbol} on {timeframe} timeframe...")
    exchange = get_exchange()
    
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # تبدیل timestamp به فرمت تاریخ خوانا
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # اطمینان از اینکه نوع داده‌ها عددی است
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])

        print("Data fetched successfully. Calculating indicators...")

        # --- روش جدید و اصلاح شده برای محاسبه و ادغام EMA یک ساعته ---

        # 1. یک کپی از دیتافریم برای محاسبات ۱ ساعته ایجاد می‌کنیم
        df_1h = df.set_index('timestamp').copy()

        # 2. داده‌ها را به تایم‌فریم ۱ ساعته Resample می‌کنیم
        df_1h = df_1h['close'].resample('1H').last().to_frame()
        
        # 3. EMA 200 را روی داده‌های ۱ ساعته محاسبه می‌کنیم
        # (به دلیل نیاز به 200 کندل، ممکن است در ابتدا مقادیر NaN داشته باشیم)
        df_1h['ema_200_1h'] = ta.ema(df_1h['close'], length=200)

        # 4. مقادیر EMA محاسبه شده را به فرکانس ۱۵ دقیقه Resample می‌کنیم.
        #    این کار به طور خودکار مقادیر را برای کندل‌های میانی پر می‌کند (forward-fill)
        df_1h_resampled = df_1h['ema_200_1h'].resample('15T').ffill()

        # 5. دیتافریم اصلی را با دیتافریم resample شده ادغام (join) می‌کنیم
        #    join بر اساس ایندکس (timestamp) کار می‌کند و بسیار امن‌تر از merge است
        df_final = df.set_index('timestamp').join(df_1h_resampled)

        # 6. سطرهایی که در ابتدای بازه زمانی به دلیل نبود داده کافی برای EMA، مقدار NaN دارند را حذف می‌کنیم
        df_final.dropna(inplace=True)
        df_final.reset_index(inplace=True)

        print("Indicators calculated and merged successfully.")
        print("Final DataFrame preview:")
        print(df_final.tail()) # یک پیش‌نمایش از ۵ سطر آخر داده نهایی چاپ می‌کنیم تا از وجود مقادیر مطمئن شویم

        return df_final

    except Exception as e:
        print(f"An error occurred in fetch_data: {e}")
        return pd.DataFrame()
