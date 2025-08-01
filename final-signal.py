import pandas as pd
import numpy as np

# فرض می‌کنیم این فایل از قبل با اندیکاتورهای لازم ساخته شده است
# df = pd.read_csv("btc_15m_with_indicators.csv")
# در اینجا یک دیتافریم نمونه برای تست می‌سازیم
data = {
    'timestamp': pd.to_datetime(pd.date_range('2023-01-01', periods=200, freq='15T')),
    'open': np.random.uniform(20000, 21000, 200),
    'high': np.random.uniform(20100, 21100, 200),
    'low': np.random.uniform(19900, 20900, 200),
    'close': np.random.uniform(20000, 21000, 200),
    'ema_200_1h': np.random.uniform(19800, 20800, 200)
}
df = pd.DataFrame(data)
# اطمینان از اینکه high بالاتر از بقیه و low پایین‌تر از بقیه است
df['high'] = df[['open', 'high', 'close']].max(axis=1) + 10
df['low'] = df[['open', 'low', 'close']].min(axis=1) - 10


# ⚙️ پارامترها
POSITION_DOLLAR = 100
MIN_BOS_PCT = 0.005
TP_PCT = 0.06 # حد سود کامل در 6%
RR_RATIO = 2 # حداقل نسبت ریسک به ریوارد برای ورود

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
order_block = {'high': 0, 'low': 0}


print("Running backtest...")
# از اندیس 2 شروع می‌کنیم تا به کندل‌های قبلی دسترسی داشته باشیم
for i in range(2, len(df)):
    # کندل‌ها
    curr = df.iloc[i]
    prev = df.iloc[i-1]
    prev_2 = df.iloc[i-2]
    price = curr['close']

    # --- مدیریت پوزیشن باز ---
    if in_position:
        # بررسی حد ضرر
        if price <= stop_loss:
            signals.append("close_sl")
            exit_prices.append(stop_loss)
            # بقیه لیست‌ها در پایان لوپ پر می‌شوند
            in_position = False
        # بررسی حد سود
        elif price >= take_profit:
            signals.append("close_tp")
            exit_prices.append(take_profit)
            in_position = False
        else:
            signals.append("hold")
            exit_prices.append(0)

    # --- منطق ورود ---
    else:
        # اگر منتظر پولبک هستیم
        if waiting_for_pullback:
            # آیا قیمت به محدوده اردربلاک پولبک زده است؟
            if curr['low'] <= order_block['high'] and curr['high'] >= order_block['low']:
                entry_price = order_block['high'] # ورود در بالای اردربلاک
                
                # محاسبه ریسک به ریوارد
                risk = entry_price - stop_loss
                reward = (entry_price * (1 + TP_PCT)) - entry_price
                
                if risk > 0 and (reward / risk) >= RR_RATIO:
                    take_profit = entry_price * (1 + TP_PCT)
                    
                    signals.append("buy")
                    exit_prices.append(0)
                    in_position = True
                    waiting_for_pullback = False # دیگر منتظر نیستیم
                else:
                    # اگر R/R مناسب نبود، سیگنال را نادیده بگیر
                    signals.append("hold")
                    exit_prices.append(0)
                    waiting_for_pullback = False
            else:
                signals.append("hold")
                exit_prices.append(0)

        # اگر منتظر سیگنال جدید هستیم
        else:
            # شرایط اولیه استراتژی
            is_uptrend = curr['close'] > curr['ema_200_1h']
            is_bos = curr['high'] > prev['high'] and (curr['high'] - prev['high']) / prev['high'] >= MIN_BOS_PCT

            if is_uptrend and is_bos:
                # اردربلاک: آخرین کندل نزولی قبل از حرکت صعودی که باعث BOS شده
                # این یک تعریف ساده شده است، prev_2 باید نزولی باشد
                if prev_2['close'] < prev_2['open']:
                    order_block['high'] = prev_2['high']
                    order_block['low'] = prev_2['low']
                    
                    # حد ضرر: زیر کفی که قبل از شکست ساختار ایجاد شده (Low کندل اردربلاک)
                    stop_loss = order_block['low']
                    
                    waiting_for_pullback = True
                    signals.append("wait_pullback") # وضعیت جدید: منتظر پولبک
                    exit_prices.append(0)
                else:
                    signals.append("hold")
                    exit_prices.append(0)
            else:
                signals.append("hold")
                exit_prices.append(0)

    # آپدیت لیست‌ها در هر تکرار
    if in_position or signals[-1] == "buy":
        entry_prices.append(entry_price)
        stop_losses.append(stop_loss)
        take_profits.append(take_profit)
    else:
        entry_prices.append(0)
        stop_losses.append(0)
        take_profits.append(0)

# ذخیره خروجی
# چون ممکن است طول لیست سیگنال‌ها با دیتافریم اصلی متفاوت باشد، باید آن را هماهنگ کنیم
final_df = df.iloc[2:].copy()
final_df['signal'] = signals
final_df['entry_price'] = entry_prices
final_df['exit_price'] = exit_prices
final_df['stop_loss'] = stop_losses
final_df['take_profit'] = take_profits

# محاسبه حجم پوزیشن (می‌تواند پویا شود)
final_df['position_size_usd'] = np.where(final_df['signal'] == 'buy', POSITION_DOLLAR, 0)

final_df.to_csv("signals_v2_with_sl_ob.csv", index=False)

print("✅ نسخه جدید 'signals_v2_with_sl_ob.csv' با منطق حد ضرر و اردربلاک ذخیره شد.")
