import ccxt
import csv
from datetime import datetime

def get_crypto_data():
    """
    اسکریپتی برای دریافت داده‌های تاریخی OHLCV از صرافی جایگزین (MEXC)
    و ذخیره آن در یک فایل CSV.
    """
    # مشخصات درخواست
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 1000
    exchange_name = 'mexc' # نام صرافی جایگزین
    output_filename = f'{exchange_name}_{symbol.replace("/", "_")}_{timeframe}.csv'
    
    # 1. اتصال به صرافی جایگزین (MEXC)
    # برای استفاده از صرافی دیگر کافیست نام آن را اینجا وارد کنید
    # مثلاً ccxt.kucoin() یا ccxt.gateio()
    exchange = getattr(ccxt, exchange_name)()

    try:
        # 2. دریافت داده‌های تاریخی OHLCV
        print(f"در حال دریافت {limit} کندل برای {symbol} از صرافی {exchange_name.upper()}...")
        
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        print("داده‌ها با موفقیت دریافت شد. در حال پردازش و ذخیره‌سازی...")

        # 3. آماده‌سازی و ذخیره داده‌ها در فایل CSV
        header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)
            
            for candle in ohlcv:
                # تبدیل timestamp به فرمت تاریخ و زمان قابل خواندن
                readable_timestamp = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                row = [readable_timestamp] + candle[1:]
                csv_writer.writerow(row)
                
        print(f"✅ عملیات با موفقیت انجام شد. داده‌ها در فایل {output_filename} ذخیره شدند.")

    # 4. مدیریت خطاهای احتمالی
    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        print(f"❌ خطا در اتصال به صرافی {exchange_name.upper()} رخ داد: {e}")
    except Exception as e:
        print(f"❌ یک خطای پیش‌بینی‌نشده رخ داد: {e}")

if __name__ == '__main__':
    get_crypto_data()