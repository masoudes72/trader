import pandas as pd
import matplotlib.pyplot as plt

# --- بارگذاری داده سیگنال‌ها ---
df = pd.read_csv("btc_signals_15m.csv")

balance = 10000
equity_curve = [balance]
in_position = False
entry_price = 0
position_size = 0
pnl_list = []

for i, row in df.iterrows():
    signal = row['signal']
    close = row['close']

    if signal == "buy" and not in_position:
        entry_price = row['entry_price']
        position_size = row['position_size']
        in_position = True

    elif signal == "sell" and in_position:
        exit_price = close
        pnl = (exit_price - entry_price) * position_size
        balance += pnl
        pnl_list.append(pnl)
        equity_curve.append(balance)
        in_position = False
        entry_price = 0
        position_size = 0

# آمار معاملات
wins = [p for p in pnl_list if p > 0]
losses = [p for p in pnl_list if p <= 0]

print("📊 خلاصه عملکرد")

print(f"\n📈 تعداد معاملات: {len(pnl_list)}")
print(f"💵 سود خالص: {sum(pnl_list):.2f} $")
print(f"✅ درصد برد: {(len(wins)/len(pnl_list)*100) if pnl_list else 0:.2f} %")
print(f"📗 مجموع سودها: {sum(wins):.2f} $")
print(f"📕 مجموع ضررها: {sum(losses):.2f} $")
print(f"🟡 میانگین سود هر معامله: {(sum(pnl_list)/len(pnl_list)) if pnl_list else 0:.2f} $")

# --- نمودار رشد سرمایه ---
plt.figure(figsize=(12, 5))
plt.plot(equity_curve, marker='o', linestyle='-', color='green', label='Equity Curve')
plt.title("📈 نمودار رشد سرمایه", fontsize=14)
plt.xlabel("تعداد معاملات بسته شده")
plt.ylabel("موجودی حساب (USD)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
