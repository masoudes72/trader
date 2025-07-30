import ccxt
import csv
from datetime import datetime

def get_crypto_data():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 1000
    exchange_name = 'binance'  # ← تغییر داده شده به بایننس
    output_filename = f'{exchange_name}_{symbol.replace("/", "_")}_{timeframe}.csv'

    exchange = getattr(ccxt, exchange_name)({
        'enableRateLimit': True
    })

    try:
        print(f"در حال دریافت {limit} کندل برای {symbol} از صرافی {exchange_name.upper()}...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

        print("✅ داده‌ها دریافت شد. در حال ذخیره‌سازی...")

        header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for candle in ohlcv:
                readable_timestamp = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([readable_timestamp] + candle[1:])

        print(f"✅ ذخیره با موفقیت: {output_filename}")

    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        print(f"❌ خطا در اتصال به {exchange_name.upper()}: {e}")
    except Exception as e:
        print(f"❌ خطای ناشناخته: {e}")

if __name__ == '__main__':
    get_crypto_data()
