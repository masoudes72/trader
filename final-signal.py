import pandas as pd

# --- پارامترهای عمومی ---
TP_RATIO = 0.02  # هدف سود
SL_RATIO = 0.01  # حد ضرر

# --- بارگذاری داده ---
df = pd.read_csv("btc_15m_with_indicators.csv")

# --- توابع ورود و خروج ---
def check_entry(prev, curr):
    """ورود به پوزیشن در صورت وجود سیگنال خرید"""
    return (
        prev['ema_9'] < prev['ema_21'] and
        curr['ema_9'] > curr['ema_21'] and
        curr['macd'] > curr['macd_signal'] and
        curr['adx'] > 20 and
        curr['close'] > curr['bb_mid']
    )

def check_exit(entry_price, curr):
    """خروج از پوزیشن در صورت رسیدن به حد سود/ضرر یا سیگنال معکوس"""
    tp_price = entry_price * (1 + TP_RATIO)
    sl_price = entry_price * (1 - SL_RATIO)

    if curr['close'] >= tp_price:
        return "tp"
    elif curr['close'] <= sl_price:
        return "sl"
    elif curr['ema_9'] < curr['ema_21']:
        return "ema_cross"
    return None

# --- تولید سیگنال ---
signals = []
entry_price = None
in_position = False

for i in range(1, len(df)):
    prev = df.iloc[i - 1]
    curr = df.iloc[i]

    if not in_position:
        if check_entry(prev, curr):
            signals.append("buy")
            entry_price = curr['close']
            in_position = True
        else:
            signals.append("hold")
    else:
        exit_reason = check_exit(entry_price, curr)
        if exit_reason:
            signals.append("sell")
            in_position = False
        else:
            signals.append("hold")

# --- ذخیره نتایج ---
df = df.iloc[1:].copy()
df['signal'] = signals
df.to_csv("btc_signals_15m.csv", index=False)

print("✅ سیگنال‌ها تولید شدند.")
print("buy:", signals.count("buy"))
print("sell:", signals.count("sell"))
print("hold:", signals.count("hold"))
