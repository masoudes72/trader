import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("btc_signals_15m.csv")

in_position = False
entry_price = 0
position_size = 0
balance = 10000
equity_curve = [balance]
trades = []

for idx, row in df.iterrows():
    signal = row['signal']
    close = row['close']

    if signal == "buy" and not in_position:
        entry_price = row['entry_price']
        position_size = row['position_size']
        in_position = True

    elif signal == "sell" and in_position:
        pnl = (close - entry_price) * position_size
        balance += pnl
        equity_curve.append(balance)

        trades.append({
            "entry_price": entry_price,
            "exit_price": close,
            "position_size": position_size,
            "pnl": pnl,
            "outcome": "win" if pnl > 0 else "loss"
        })

        in_position = False
        entry_price = 0
        position_size = 0

# در صورت باز بودن معامله آخر
if in_position:
    pnl = (df.iloc[-1]['close'] - entry_price) * position_size
    balance += pnl
    equity_curve.append(balance)
    trades.append({
        "entry_price": entry_price,
        "exit_price": df.iloc[-1]['close'],
        "position_size": position_size,
        "pnl": pnl,
        "outcome": "win" if pnl > 0 else "loss"
    })

# محاسبه آمار نهایی
trades_df = pd.DataFrame(trades)
wins = trades_df[trades_df['pnl'] > 0]
losses = trades_df[trades_df['pnl'] <= 0]

print("📊 خلاصه عملکرد واقعی با درنظر گرفتن حجم پوزیشن:\n")
print(f"📈 تعداد معاملات: {len(trades)}")
print(f"✅ درصد برد: {len(wins)/len(trades)*100:.2f} %")
print(f"📗 مجموع سودها: {wins['pnl'].sum():.2f} $")
print(f"📕 مجموع ضررها: {losses['pnl'].sum():.2f} $")
print(f"💵 سود خالص: {trades_df['pnl'].sum():.2f} $")
print(f"🟡 میانگین سود/ضرر هر معامله: {trades_df['pnl'].mean():.2f} $")

# نمودار رشد سرمایه
plt.figure(figsize=(12, 6))
plt.plot(equity_curve, marker="o", color="green", label="Equity")
plt.title("📈 نمودار رشد سرمایه (Equity Curve)", fontsize=14)
plt.xlabel("تعداد معاملات بسته‌شده", fontsize=12)
plt.ylabel("موجودی (USD)", fontsize=12)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
