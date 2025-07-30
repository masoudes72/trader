import pandas as pd
import os

input_file = 'btc_15m_with_indicators.csv'
output_file = 'btc_signals_15m.csv'

try:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"فایل '{input_file}' یافت نشد.")

    df = pd.read_csv(input_file)

    # بررسی وجود ستون‌ها
    required_columns = {'ema_9', 'ema_21', 'rsi_14'}
    if not required_columns.issubset(df.columns):
        raise ValueError("فرمت فایل اشتباه است. ستون‌های ema_9، ema_21 و rsi_14 باید وجود داشته باشند.")

    # حذف ردیف‌های دارای NaN در ستون‌های مهم
    df.dropna(subset=['ema_9', 'ema_21', 'rsi_14'], inplace=True)

    # ساخت ستون signal
    def generate_signal(row):
        if row['ema_9'] > row['ema_21'] and row['rsi_14'] < 70:
            return 'buy'
        elif row['ema_9'] < row['ema_21'] and row['rsi_14'] > 30:
            return 'sell'
        else:
            return 'hold'

    df['signal'] = df.apply(generate_signal, axis=1)

    # ذخیره فایل خروجی
    df.to_csv(output_file, index=False)

    # شمارش سیگنال‌ها
    signal_counts = df['signal'].value_counts()
    print("تعداد سیگنال‌ها:")
    for signal in ['buy', 'sell', 'hold']:
        print(f"{signal}: {signal_counts.get(signal, 0)}")

except FileNotFoundError as e:
    print(e)
except ValueError as e:
    print(e)
except Exception as e:
    print(f"خطای غیرمنتظره: {e}")
