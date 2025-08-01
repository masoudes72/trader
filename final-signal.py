import pandas as pd
import numpy as np

# شما باید فایل اصلی خود را جایگزین کنید
# df = pd.read_csv("btc_15m_with_indicators.csv")
# استفاده از داده‌های نمونه برای نمایش عملکرد
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
RR_RATIO = 1.5
SWING_LOW_LOOKBACK = 10
FIB_OTE_MIN = 0.62
FIB_OTE_MAX = 0.79

# ... متغیرهای خروجی ...
signals = []
entry_prices, exit_prices, stop_losses, take_profits = [], [], [], []

# 🤖 وضعیت ربات
in_position = False
waiting_for_pullback = False
entry_price, stop_loss, take_profit = 0.0, 0.0, 0.0
impulse_high, impulse_low = 0.0, 0.0
ote_zone = {'high': 0, 'low': 0}

print("Running backtest v3.1 (DEBUG MODE)...")
for i in range(SWING_LOW_LOOKBACK, len(df)):
    curr = df.iloc[i]
    prev = df.iloc[i-1]
    price = curr['close']
    timestamp = curr['timestamp']

    # --- مدیریت پوزیشن باز ---
    if in_position:
        if price <= stop_loss:
            print(f"🔴 {timestamp}: CLOSE_SL triggered at price {price:.2f}")
            signals.append("close_sl")
            exit_prices.append(stop_loss)
            in_position = False
        elif price >= take_profit:
            print(f"✅ {timestamp}: CLOSE_TP triggered at price {price:.2f}")
            signals.append("close_tp")
            exit_prices.append(take_profit)
            in_position = False
        else:
            signals.append("hold")
            exit_prices.append(0)
    # --- منطق ورود ---
    else:
        if waiting_for_pullback:
            print(f"⏳ {timestamp}: Waiting for pullback. Price: {price:.2f}. OTE Zone: [{ote_zone['low']:.2f} - {ote_zone['high']:.2f}]")
            if curr['low'] <= ote_zone['high'] and curr['high'] >= ote_zone['low']:
                entry_price = ote_zone['high']
                risk = entry_price - stop_loss
                reward = (entry_price * (1 + TP_PCT)) - entry_price
                
                if risk > 0 and (reward / risk) >= RR_RATIO:
                    take_profit = entry_price * (1 + TP_PCT)
                    print(f"🎯 {timestamp}: OTE TRIGGERED! Preparing BUY order.")
                    print(f"   Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}, R/R: {reward/risk:.2f}")
                    signals.append("buy")
                    exit_prices.append(0)
                    in_position = True
                    waiting_for_pullback = False
                else:
                    print(f"❌ {timestamp}: OTE triggered but R/R ratio too low ({reward/risk:.2f}). Signal invalidated.")
                    signals.append("hold")
                    exit_prices.append(0)
                    waiting_for_pullback = False
            elif curr['high'] > impulse_high:
                 print(f"❌ {timestamp}: Price broke impulse high ({impulse_high:.2f}) before pullback. Signal invalidated.")
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
                swing_low_candle_range = df.iloc[i - SWING_LOW_LOOKBACK : i]
                impulse_low_price = swing_low_candle_range['low'].min()
                impulse_high_price = curr['high']
                
                impulse_range = impulse_high_price - impulse_low_price
                ote_zone['high'] = impulse_high_price - (impulse_range * FIB_OTE_MIN)
                ote_zone['low'] = impulse_high_price - (impulse_range * FIB_OTE_MAX)

                stop_loss = impulse_low_price
                impulse_high = impulse_high_price
                
                print(f"🔍 {timestamp}: BOS DETECTED! Price: {price:.2f}")
                print(f"   Impulse: [{impulse_low_price:.2f} -> {impulse_high_price:.2f}]")
                print(f"   Calculated OTE Zone: [{ote_zone['low']:.2f} - {ote_zone['high']:.2f}]")
                
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

final_df = df.iloc[SWING_LOW_LOOKBACK:].copy()
final_df['signal'] = signals
# ... بقیه کد برای ذخیره فایل ...
final_df.to_csv("signals_v3_debug.csv", index=False)
print("✅ نسخه دیباگ 'signals_v3_debug.csv' ذخیره شد.")
