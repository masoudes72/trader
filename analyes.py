import pandas as pd

# بارگذاری داده‌های اندیکاتور
df = pd.read_csv("btc_15m_with_indicators.csv")

# بررسی اینکه ستون‌های مورد نیاز وجود دارند یا محاسبه شوند
if 'atr' not in df.columns:
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['atr'] = df['TR'].rolling(window=14).mean()

if 'momentum' not in df.columns:
    df['momentum'] = df['close'] - df['close'].shift(4)

signals = []
in_position = False
entry_price = None

for i in range(20, len(df)):
    close = df['close'].iloc[i]
    upper = df['bb_upper'].iloc[i]
    bb_std = df['bb_std'].iloc[i]
    momentum = df['momentum'].iloc[i]
    atr = df['atr'].iloc[i]

    recent_std = df['bb_std'].iloc[i-3:i].mean()

    if not in_position:
        if (close > upper) and (recent_std < bb_std) and (momentum > 0):
            signals.append("buy")
            entry_price = close
            in_position = True
        else:
            signals.append("hold")
    else:
        tp = entry_price + 2.5 * atr
        sl = entry_price - 1.25 * atr

        if close >= tp:
            signals.append("sell")  # Take Profit
            in_position = False
        elif close <= sl:
            signals.append("sell")  # Stop Loss
            in_position = False
        elif momentum < 0:
            signals.append("sell")  # خروج بر اساس کاهش مومنتوم
            in_position = False
        else:
            signals.append("hold")

# هماهنگ کردن طول سیگنال‌ها با دیتافریم
df = df.iloc[20:].copy()
df['signal'] = signals

# ذخیره فایل نهایی سیگنال‌ها
df.to_csv("btc_signals_15m.csv", index=False)

print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
