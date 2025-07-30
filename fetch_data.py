import ccxt
import csv
from datetime import datetime

def get_crypto_data():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 1000
    exchange_name = 'binance'
    output_filename = f'{exchange_name}_{symbol.replace("/", "_")}_{timeframe}.csv'

    print("🚀 شروع دریافت اطلاعات از Binance...")

    try:
        exchange = getattr(ccxt, exchange_name)({
            'enableRateLimit': True
        })

        print(f"📡 در حال درخواست {limit} کندل برای {symbol}...")

        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

        if not ohlcv:
            print("⚠️ خروجی ohlcv خالی است! ممکن است مشکل از صرافی یا محدودیت IP باشد.")
            return

        print(f"✅ {len(ohlcv)} کندل دریافت شد.")
        print("📝 در حال نوشتن در فایل...")

        header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for candle in ohlcv:
                readable_timestamp = datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([readable_timestamp] + candle[1:])

        print(f"📁 ذخیره شد در فایل: {output_filename}")

    except Exception as e:
        print(f"❌ خطا در دریافت داده: {str(e)}")

if __name__ == '__main__':
    get_crypto_data()
