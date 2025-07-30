import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import importlib.util
import os

st.set_page_config(page_title="📊 داشبورد سیگنال رمزارز", layout="wide")
st.title("📈 داشبورد تحلیلی رمزارز - نسخه دیباگ")

st.markdown("### 🔧 بررسی مرحله‌ای با گزارش دقیق")

# اجرای فایل پایتون با importlib
import subprocess

def run_script(script_name, label):
    try:
        st.info(f"⏳ اجرای {label}...")
        result = subprocess.run(["python", script_name], capture_output=True, text=True)
        
        # وضعیت اجرا
        if result.returncode == 0:
            st.success(f"✅ {label} با موفقیت اجرا شد.")
        else:
            st.error(f"❌ خطا در اجرای {label} (exit code {result.returncode})")
        
        # خروجی استاندارد (stdout)
        if result.stdout:
            st.markdown("**📤 خروجی برنامه:**")
            st.code(result.stdout, language="bash")

        # خطاهای استاندارد (stderr)
        if result.stderr:
            st.markdown("**❗ خطا:**")
            st.code(result.stderr, language="bash")

    except Exception as e:
        st.error(f"❌ اجرای فایل {script_name} با خطای کلی مواجه شد.")
        st.exception(e)

# دکمه‌ها برای اجرای مراحل
with st.expander("🎛 اجرای مراحل تحلیل"):
    if st.button("📥 مرحله ۱: دریافت داده (fetch_data.py)"):
        run_script("fetch_data.py", "دریافت داده")

    if st.button("📊 مرحله ۲: محاسبه اندیکاتورها (analyes.py)"):
        run_script("analyes.py", "محاسبه اندیکاتورها")

    if st.button("📈 مرحله ۳: تولید سیگنال (final-signal.py)"):
        run_script("final-signal.py", "تولید سیگنال")

    if st.button("💰 مرحله ۴: تحلیل نهایی (result.py)"):
        run_script("result.py", "تحلیل معاملات")

    if st.button("🔄 اجرای همه مراحل"):
        for script, label in [
            ("fetch_data.py", "دریافت داده"),
            ("analyes.py", "محاسبه اندیکاتورها"),
            ("final-signal.py", "تولید سیگنال"),
            ("result.py", "تحلیل معاملات"),
        ]:
            run_script(script, label)

st.markdown("---")

# بررسی وجود فایل‌های میانی
with st.expander("📂 بررسی فایل‌های خروجی"):
    files = [
        "mexc_BTC_USDT_15m.csv",
        "btc_15m_with_indicators.csv",
        "btc_signals_15m.csv"
    ]
    for file in files:
        if os.path.exists(file):
            st.success(f"✅ فایل وجود دارد: `{file}`")
        else:
            st.warning(f"❌ فایل پیدا نشد: `{file}`")

# نمایش محتوا و ستون‌های فایل اندیکاتورها
if os.path.exists("btc_15m_with_indicators.csv"):
    st.subheader("📄 بررسی فایل اندیکاتورها")
    df_ind = pd.read_csv("btc_15m_with_indicators.csv")
    st.write("ستون‌های موجود:", df_ind.columns.tolist())
    st.dataframe(df_ind.tail(10))

# بررسی و نمایش سیگنال‌ها
if os.path.exists("btc_signals_15m.csv"):
    st.subheader("📋 جدول سیگنال‌های تولید شده")
    df_sig = pd.read_csv("btc_signals_15m.csv")
    st.dataframe(df_sig.tail(15))

    if 'signal' not in df_sig.columns or 'close' not in df_sig.columns:
        st.error("⛔ فایل سیگنال ستون‌های ضروری (`signal`, `close`) را ندارد.")
    else:
        signal_counts = df_sig['signal'].value_counts()
        st.write("✅ آمار سیگنال‌ها:")
        for s in ['buy', 'sell', 'hold']:
            st.write(f"• {s}: {signal_counts.get(s, 0)}")

        if signal_counts.get("buy", 0) == 0 and signal_counts.get("sell", 0) == 0:
            st.warning("⚠️ هیچ سیگنال buy یا sell تولید نشده. شاید شرط‌های سیگنال‌دهی سختگیرانه باشن.")

# تحلیل معاملات نهایی
if os.path.exists("btc_signals_15m.csv"):
    df = pd.read_csv("btc_signals_15m.csv")
    if "signal" in df.columns and "close" in df.columns:
        st.subheader("📊 تحلیل معاملات")

        trades = []
        in_position = False
        entry_price = 0.0

        for _, row in df.iterrows():
            if row["signal"] == "buy" and not in_position:
                entry_price = row["close"]
                in_position = True
            elif row["signal"] == "sell" and in_position:
                trades.append(row["close"] - entry_price)
                in_position = False

        if in_position:
            trades.append(df.iloc[-1]["close"] - entry_price)

        num_trades = len(trades)
        profits = [p for p in trades if p > 0]
        losses = [p for p in trades if p <= 0]
        total_profit = sum(profits)
        total_loss = sum(losses)
        net_profit = total_profit + total_loss
        avg_profit = net_profit / num_trades if num_trades > 0 else 0
        win_rate = (len(profits) / num_trades * 100) if num_trades > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("📈 تعداد معاملات", num_trades)
        col2.metric("💵 سود خالص", f"{net_profit:.2f} $")
        col3.metric("✅ درصد سوددهی", f"{win_rate:.2f}%")

        col4, col5 = st.columns(2)
        col4.metric("📗 مجموع سودها", f"{total_profit:.2f} $")
        col5.metric("📕 مجموع ضررها", f"{total_loss:.2f} $")

        st.write(f"🔸 میانگین سود هر معامله: `{avg_profit:.2f} $`")

        # نمودار رشد سرمایه
        equity = [1000]
        for pnl in trades:
            equity.append(equity[-1] + pnl)

        st.subheader("📈 نمودار رشد سرمایه")
        fig, ax = plt.subplots()
        ax.plot(equity, marker="o", color="green")
        ax.set_title("نمودار رشد سرمایه (Equity Curve)")
        ax.set_xlabel("تعداد معاملات")
        ax.set_ylabel("سرمایه (دلار)")
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.error("⛔ فایل سیگنال برای تحلیل قابل استفاده نیست (ستون‌های ناقص).")
