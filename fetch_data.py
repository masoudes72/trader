# محتوای کامل برای فایل fetch_data.py (بدون نیاز به pandas-ta)

import ccxt
import pandas as pd

def get_exchange():
    return ccxt.binance({
        'rateLimit': 1200,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })

def fetch_data(symbol='BTC/USDT', timeframe='5m', limit=2000):
    """
    داده‌های قیمت را دریافت کرده و اندیکاتورهای لازم را به صورت دستی محاسبه می‌کند.
    """
    print(f"Fetching {limit} candles for {symbol} on {timeframe} timeframe...")
    exchange = get_exchange()
    
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])

        print("Data fetched successfully. Calculating indicators manually...")

        # --- روش محاسبه دستی EMA با استفاده از خود Pandas ---

        # 1. کپی و تبدیل داده به تایم‌فریم ۱ ساعته
        df_1h = df.set_index('timestamp').copy()
        df_1h = df_1h['close'].resample('1H').last().to_frame()
        
        # 2. محاسبه دستی EMA 200 با تابع .ewm() خود pandas
        df_1h['ema_200_1h'] = df_1h['close'].ewm(span=200, adjust=False).mean()

        # 3. Resample کردن EMA یک ساعته به فرکانس ۱۵ دقیقه
        df_1h_resampled = df_1h['ema_200_1h'].resample('15T').ffill()

        # 4. ادغام با دیتافریم اصلی
        df_final = df.set_index('timestamp').join(df_1h_resampled)

        # 5. حذف سطرهای خالی اولیه
        df_final.dropna(inplace=True)
        df_final.reset_index(inplace=True)

        print("Indicators calculated and merged successfully.")
        print("Final DataFrame preview:")
        print(df_final.tail())

        return df_final

    except Exception as e:
        print(f"An error occurred in fetch_data: {e}")
        return pd.DataFrame()

