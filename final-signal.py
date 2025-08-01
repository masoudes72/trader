import pandas as pd

# بارگذاری دیتاست اصلی با اندیکاتورها
df = pd.read_csv("btc_15m_with_indicators.csv")

# پارامترها
POSITION_DOLLAR = 100

# متغیرهای خروجی
signals = []
entry_prices = []
exit_prices = []
position_sizes = []

# متغیرهای کنترلی وضعیت
in_position = False
entry_price = 0.0
position_size = 0.0

# شروع از کندل سوم به بعد برای مقایسه با کندل قبلی
for i in range(2, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i - 1]
    price = curr['close']

    # شرط ورود
    bias_up = curr['close'] > curr['ema_200_1h']
    bos_simple = curr['high'] > prev['high']

    if not in_position:
        if bias_up and bos_simple:
            entry_price = price
            position_size = POSITION_DOLLAR / entry_price
            in_position = True

            signals.append("buy")
            entry_prices.append(entry_price)
            exit_prices.append(0)
            position_sizes.append(round(position_size, 4))
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

    else:
        # شرط خروج: BOS نزولی ساده
        bos_down = curr['low'] < prev['low']
        if bos_down:
            signals.append("sell")
            exit_prices.append(price)
            entry_prices.append(entry_price)          # حفظ مقدار ورود
            position_sizes.append(round(position_size, 4))  # حفظ حجم
            in_position = False
            entry_price = 0
            position_size = 0
        else:
            signals.append("hold")
            entry_prices.append(0)
            exit_prices.append(0)
            position_sizes.append(0)

# تولید فایل خروجی
df = df.iloc[2:].copy()
df['signal'] = signals
df['entry_price'] = entry_prices
df['exit_price'] = exit_prices
df['position_size'] = position_sizes
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ فایل final-signal.py اجرا شد و سیگنال‌ها در btc_signals_15m.csv ذخیره شدند.")
