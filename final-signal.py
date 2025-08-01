import pandas as pd
import numpy as np

# این بخش برای تست است و شما باید فایل اصلی خود را جایگزین کنید
# df = pd.read_csv("btc_15m_with_indicators.csv")
data = {
    'timestamp': pd.to_datetime(pd.date_range('2023-01-01', periods=400, freq='15T')),
    'open': np.random.uniform(20000, 21000, 400),
    'high': np.random.uniform(20100, 21100, 400),
    'low': np.random.uniform(19900, 20900, 400),
    'close': np.random.uniform(20000, 21000, 400),
    'ema_200_1h': pd.Series(np.random.uniform(19800, 20800, 400)).rolling(window=20).mean()
}
df = pd.DataFrame(data)
df['high'] = df[['open', 'high', 'close']].max(axis=1) + 10
df['low'] = df[['open', 'low', 'close']].min(axis=1) - 10
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)


# ⚙️ پارامترها
POSITION_DOLLAR = 100
MIN_BOS_PCT = 0.005
TP_PCT = 0.06
RR_RATIO = 1.5  # نسبت ریسک به ریوارد را کمی کاهش دادیم تا انعطاف بیشتر شود
SWING_LOW_LOOKBACK = 10 # تعداد کندل برای یافتن کف قبلی
FIB_OTE_MIN = 0.62 # سطح فیبوناچی برای شروع ناحیه OTE
FIB_OTE_MAX = 0.79 # سطح فیبوناچی برای پایان ناحیه OTE

# 📊 متغیرهای خروجی
signals = []
entry_prices = []
exit_prices = []
stop_losses = []
take_profits = []

# 🤖 وضعیت ربات
in_position = False
waiting_for_pullback = False
entry_price = 0.0
stop_loss = 0.0
take_profit = 0.0
impulse_high = 0.0
impulse_low = 0.0
ote_zone = {'high': 0, 'low': 0}

print("Running backtest v3 with Swing Low and OTE...")
for i in range(SWING_LOW_LOOKBACK, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i-1]
    price = curr['close']

    # --- مدیریت پوزیشن باز ---
    if in_position:
        if price <= stop_loss:
            signals.append("close_sl")
            exit_prices.append(stop_loss)
            in_position = False
        elif price >= take_profit:
            signals.append("close_tp")
            exit_prices.append(take_profit)
            in_position = False
        else:
            signals.append("hold")
            exit_prices.append(0)
    # --- منطق ورود ---
    else:
        if waiting_for_pullback:
            # آیا قیمت وارد ناحیه OTE شده است؟
            if curr['low'] <= ote_zone['high'] and curr['high'] >= ote_zone['low']:
                entry_price = ote_zone['high'] # ورود در بالای ناحیه OTE
                
                # محاسبه ریسک به ریوارد
                risk = entry_price - stop_loss
                reward = (entry_price * (1 + TP_PCT)) - entry_price
                
                if risk > 0 and (reward / risk) >= RR_RATIO:
                    take_profit = entry_price * (1 + TP_PCT)
                    
                    signals.append("buy")
                    exit_prices.append(0)
                    in_position = True
                    waiting_for_pullback = False
                else:
                    signals.append("hold")
                    exit_prices.append(0)
                    waiting_for_pullback = False # سیگنال نامعتبر شد
            # اگر قیمت بدون پولبک زدن، سقف قبلی را هم بشکند، سیگنال نامعتبر است
            elif curr['high'] > impulse_high:
                 signals.append("hold")
                 exit_prices.append(0)
                 waiting_for_pullback = False
            else:
                signals.append("hold")
                exit_prices.append(0)

        else:
            is_uptrend = curr['close'] > curr['ema_200_1h']
            is_bos = curr['high'] > prev['high'] and (curr['high'] - prev['high']) / prev['high'] >= MIN_BOS_PCT

            if is_uptrend and is_bos:
                # یافتن Swing Low در 10 کندل گذشته
                swing_low_candle_range = df.iloc[i - SWING_LOW_LOOKBACK : i]
                impulse_low_price = swing_low_candle_range['low'].min()
                
                # یافتن شروع حرکت ایمپالس (کندلی که Swing Low را ثبت کرده)
                impulse_start_index = swing_low_candle_range['low'].idxmin()

                # حرکت ایمپالس از Swing Low تا کندلی است که BOS را ساخته
                impulse_high_price = curr['high']
                
                # محاسبه ناحیه OTE با فیبوناچی
                impulse_range = impulse_high_price - impulse_low_price
                ote_zone['high'] = impulse_high_price - (impulse_range * FIB_OTE_MIN)
                ote_zone['low'] = impulse_high_price - (impulse_range * FIB_OTE_MAX)

                # تنظیم پارامترها برای انتظار
                stop_loss = impulse_low_price
                impulse_high = impulse_high_price
                
                waiting_for_pullback = True
                signals.append("wait_pullback")
                exit_prices.append(0)
            else:
                signals.append("hold")
                exit_prices.append(0)

    # آپدیت لیست‌ها
    if in_position or signals[-1] == "buy":
        entry_prices.append(entry_price)
        stop_losses.append(stop_loss)
        take_profits.append(take_profit)
    else:
        entry_prices.append(0)
        stop_losses.append(0)
        take_profits.append(0)

# ذخیره خروجی
final_df = df.iloc[SWING_LOW_LOOKBACK:].copy()
final_df['signal'] = signals
final_df['entry_price'] = entry_prices
final_df['exit_price'] = exit_prices
final_df['stop_loss'] = stop_losses
final_df['take_profit'] = take_profits
final_df['position_size_usd'] = np.where(final_df['signal'] == 'buy', POSITION_DOLLAR, 0)

final_df.to_csv("signals_v3_with_ote.csv", index=False)

print("✅ نسخه جدید 'signals_v3_with_ote.csv' با منطق Swing Low و OTE ذخیره شد.")
