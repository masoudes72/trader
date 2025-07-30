import pandas as pd

# بارگذاری داده‌های اندیکاتور
df = pd.read_csv("btc_15m_with_indicators.csv")

# محاسبه ATR و Momentum اگر در فایل نیست
if 'atr' not in df.columns:
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['atr'] = df['TR'].rolling(window=14).mean()

if 'momentum' not in df.columns:
    df['momentum'] = df['close'] - df['close'].shift(4)

# تولید سیگنال‌ها بر اساس شکست نوسان و مومنتوم
signals = []
in_position = False
entry_price = None

for i in range(14, len(df)):
    close_now = df['close'].iloc[i]
    close_past = df['close'].iloc[i-3]
    atr = df['atr'].iloc[i]
    momentum = df['momentum'].iloc[i]

    if not in_position:
        if (close_now - close_past > 1.5 * atr) and (momentum > 0):
            signals.append("buy")
            entry_price = close_now
            in_position = True
        else:
            signals.append("hold")
    else:
        tp = entry_price + 2.5 * atr
        sl = entry_price - 1.2 * atr

        if close_now >= tp:
            signals.append("sell")  # Take profit
            in_position = False
        elif close_now <= sl:
            signals.append("sell")  # Stop loss
            in_position = False
        elif momentum < 0:
            signals.append("sell")  # خروج با برگشت مومنتوم
            in_position = False
        else:
            signals.append("hold")

# تطابق طول دیتافریم با سیگنال‌ها
df = df.iloc[14:].copy()
df['signal'] = signals

# ذخیره سیگنال‌ها
df.to_csv("btc_signals_15m.csv", index=False)

print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
