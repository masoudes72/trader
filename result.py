import pandas as pd
import matplotlib.pyplot as plt
import os

input_file = 'btc_signals_15m.csv'

try:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"فایل '{input_file}' یافت نشد.")

    df = pd.read_csv(input_file)

    if 'signal' not in df.columns or 'close' not in df.columns:
        raise ValueError("فایل باید دارای ستون‌های 'signal' و 'close' باشد.")

    trades = []
    in_position = False
    entry_price = 0.0

    for _, row in df.iterrows():
        signal = row['signal']
        price = row['close']

        if signal == 'buy' and not in_position:
            entry_price = price
            in_position = True

        elif signal == 'sell' and in_position:
            exit_price = price
            pnl = exit_price - entry_price
            trades.append(pnl)
            in_position = False

    # ✅ بستن پوزیشن باز در انتهای فایل با آخرین قیمت
    if in_position:
        final_price = df.iloc[-1]['close']
        pnl = final_price - entry_price
        trades.append(pnl)

    # محاسبه آمار
    num_trades = len(trades)
    profits = [p for p in trades if p > 0]
    losses = [p for p in trades if p <= 0]
    total_profit = sum(profits)
    total_loss = sum(losses)
    net_profit = total_profit + total_loss
    avg_profit = net_profit / num_trades if num_trades > 0 else 0
    win_rate = (len(profits) / num_trades * 100) if num_trades > 0 else 0

    # محاسبه رشد سرمایه
    equity = [1000]
    for pnl in trades:
        equity.append(equity[-1] + pnl)

    # نمایش نتایج
    print(f"تعداد معاملات: {num_trades}")
    print(f"مجموع سود: {total_profit:.2f}")
    print(f"مجموع ضرر: {total_loss:.2f}")
    print(f"سود خالص: {net_profit:.2f}")
    print(f"میانگین سود هر معامله: {avg_profit:.2f}")
    print(f"درصد معاملات سودده: {win_rate:.2f}%")

    # رسم نمودار رشد سرمایه
    plt.figure(figsize=(10, 6))
    plt.plot(equity, marker='o')
    plt.title('نمودار رشد سرمایه (Equity Curve)')
    plt.xlabel('تعداد معاملات')
    plt.ylabel('سرمایه (دلار)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

except FileNotFoundError as e:
    print(e)
except ValueError as e:
    print(e)
except Exception as e:
    import traceback
    traceback.print_exc()
