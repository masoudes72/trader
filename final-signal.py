import pandas as pd
import numpy as np

# شما باید فایل اصلی خود را جایگزین کنید
df = pd.read_csv("btc_15m_with_indicators.csv") # <--- فایل خودتان را اینجا قرار دهید

# ⚙️ پارامترها
POSITION_DOLLAR = 100
MIN_BOS_PCT = 0.002 # <--- کاهش حساسیت
TP_PCT = 0.04 # <--- حد سود کمی واقع‌گرایانه‌تر شد
RR_RATIO = 1.5
LOOKBACK = 10 # تغییر نام برای وضوح بیشتر
FIB_OTE_MIN = 0.62
FIB_OTE_MAX = 0.79

# 📊 متغیرهای خروجی
signals, entry_prices, exit_prices, stop_losses, take_profits = [], [], [], [], []

# 🤖 وضعیت ربات
position_type = None # می‌تواند 'long', 'short' یا None باشد
waiting_for_pullback = False
# ... بقیه متغیرهای وضعیت ...
entry_price, stop_loss, take_profit = 0.0, 0.0, 0.0
impulse_point = 0.0 # High برای Long و Low برای Short
pullback_trigger_price = 0.0
ote_zone = {'high': 0, 'low': 0}

print("Running backtest v4 (Long & Short Strategy)...")
for i in range(LOOKBACK, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i-1]
    price = curr['close']

    # --- مدیریت پوزیشن باز ---
    if position_type is not None:
        if position_type == 'long':
            if price <= stop_loss:
                signals.append("close_sl_long")
                exit_prices.append(stop_loss)
                position_type = None
            elif price >= take_profit:
                signals.append("close_tp_long")
                exit_prices.append(take_profit)
                position_type = None
            else:
                signals.append("hold_long")
                exit_prices.append(0)
        elif position_type == 'short':
            if price >= stop_loss:
                signals.append("close_sl_short")
                exit_prices.append(stop_loss)
                position_type = None
            elif price <= take_profit:
                signals.append("close_tp_short")
                exit_prices.append(take_profit)
                position_type = None
            else:
                signals.append("hold_short")
                exit_prices.append(0)
    # --- منطق ورود ---
    else:
        if waiting_for_pullback:
            # منطق پولبک برای هر دو حالت خرید و فروش
            # ... (برای سادگی در این نسخه حذف شده، می‌توان بعدا اضافه کرد)
            signals.append("hold")
            exit_prices.append(0)
            waiting_for_pullback = False # فعلا منطق پولبک را غیرفعال میکنیم تا سیگنال اولیه را ببینیم
        else:
            # --- بررسی برای سیگنال خرید (Long) ---
            is_uptrend = curr['close'] > curr['ema_200_1h']
            is_bos_up = curr['high'] > prev['high'] and (curr['high'] - prev['high']) / prev['high'] >= MIN_BOS_PCT
            
            if is_uptrend and is_bos_up:
                swing_low = df.iloc[i - LOOKBACK : i]['low'].min()
                entry_price = price
                stop_loss = swing_low
                take_profit = entry_price * (1 + TP_PCT)
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
                
                if risk > 0 and (reward / risk) >= RR_RATIO:
                    signals.append("buy")
                    exit_prices.append(0)
                    position_type = 'long'
                else:
                    signals.append("hold")
                    exit_prices.append(0)

            # --- بررسی برای سیگنال فروش (Short) ---
            elif curr['close'] < curr['ema_200_1h']:
                is_bos_down = curr['low'] < prev['low'] and (prev['low'] - curr['low']) / curr['low'] >= MIN_BOS_PCT
                if is_bos_down:
                    swing_high = df.iloc[i - LOOKBACK : i]['high'].max()
                    entry_price = price
                    stop_loss = swing_high
                    take_profit = entry_price * (1 - TP_PCT)
                    risk = stop_loss - entry_price
                    reward = entry_price - take_profit
                    
                    if risk > 0 and (reward / risk) >= RR_RATIO:
                        signals.append("sell") # سیگنال فروش
                        exit_prices.append(0)
                        position_type = 'short'
                    else:
                        signals.append("hold")
                        exit_prices.append(0)
                else:
                    signals.append("hold")
                    exit_prices.append(0)
            else:
                signals.append("hold")
                exit_prices.append(0)

    # آپدیت لیست‌ها
    if position_type is not None and "close" not in signals[-1]:
        entry_prices.append(entry_price)
        stop_losses.append(stop_loss)
        take_profits.append(take_profit)
    else:
        entry_prices.append(0)
        stop_losses.append(0)
        take_profits.append(0)

# ذخیره خروجی
final_df = df.iloc[LOOKBACK:].copy()
final_df['signal'] = signals
final_df['entry_price'] = entry_prices
final_df['exit_price'] = exit_prices
final_df['stop_loss'] = stop_losses
final_df['take_profit'] = take_profits

final_df.to_csv("signals_v4_long_short.csv", index=False)
print("✅ نسخه جدید 'signals_v4_long_short.csv' با استراتژی دو طرفه ذخیره شد.")
