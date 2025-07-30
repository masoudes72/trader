import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import importlib.util
import os
import time

st.set_page_config(page_title="داشبورد سیگنال رمزارز", layout="wide")

# ✅ هدر بالا
st.markdown("""
<style>
h1 {
    text-align: center;
    color: #2c3e50;
}
div.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 داشبورد تحلیل، سیگنال‌گیری و ارزیابی رمزارز")
st.markdown("🔹 تحلیل تکنیکال و ارزیابی عملکرد بر اساس اندیکاتورها و سیگنال‌های هوشمند")

st.markdown("---")

# ✅ اجرای فایل‌ها با importlib
def run_script(script_name, label):
    try:
        with st.spinner(f"⏳ اجرای {label}..."):
            file_path = f"./{script_name}"
            spec = importlib.util.spec_from_file_location("module.name", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            time.sleep(1)
        st.success(f"✅ {label} با موفقیت انجام شد.")
    except Exception as e:
        st.error(f"❌ خطا در اجرای {label}")
        st.exception(e)

# ✅ بخش دکمه‌ها
with st.expander("⚙️ اجرای مراحل تحلیل و سیگنال‌دهی", expanded=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📥 مرحله ۱: دریافت داده"):
            run_script("fetch_data.py", "دریافت داده")

        if st.button("📊 مرحله ۲: محاسبه اندیکاتورها"):
            run_script("analyes.py", "محاسبه اندیکاتورها")

    with col2:
        if st.button("📈 مرحله ۳: تولید سیگنال"):
            run_script("final-signal.py", "تولید سیگنال")

        if st.button("💰 مرحله ۴: تحلیل عملکرد"):
            run_script("result.py", "تحلیل معاملات")

    with col3:
        if st.button("🔄 اجرای کامل (۱ تا ۴)"):
            for script, label in [
                ("fetch_data.py", "دریافت داده"),
                ("analyes.py", "محاسبه اندیکاتورها"),
                ("final-signal.py", "تولید سیگنال"),
                ("result.py", "تحلیل معاملات"),
            ]:
                run_script(script, label)

st.markdown("---")

# ✅ نمایش آخرین سیگنال‌ها
if os.path.exists("btc_signals_15m.csv"):
    df = pd.read_csv("btc_signals_15m.csv")
    st.subheader("📋 سیگنال‌های اخیر")
    st.dataframe(df.tail(15), use_container_width=True)

# ✅ تحلیل معاملات و نمایش آمار
if os.path.exists("btc_signals_15m.csv"):
    df = pd.read_csv("btc_signals_15m.csv")
    if "signal" in df.columns and "close" in df.columns:
        st.subheader("📊 ارزیابی استراتژی")

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

        # 📦 نمایش کارت‌های آمار
        st.markdown("### 📊 خلاصه عملکرد")
        col1, col2, col3 = st.columns(3)
        col1.metric("تعداد معاملات", num_trades)
        col2.metric("سود خالص", f"{net_profit:.2f} $")
        col3.metric("درصد برد", f"{win_rate:.2f} %")

        col4, col5 = st.columns(2)
        col4.metric("📗 مجموع سودها", f"{total_profit:.2f} $")
        col5.metric("📕 مجموع ضررها", f"{total_loss:.2f} $")

        st.markdown(f"🟡 میانگین سود هر معامله: `{avg_profit:.2f} $`")

        # ✅ نمودار رشد سرمایه
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
