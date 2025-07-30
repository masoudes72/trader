import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import importlib.util
import os

st.set_page_config(page_title="داشبورد سیگنال رمزارز", layout="centered")
st.title("📈 داشبورد تحلیل و سیگنال رمزارز")
st.markdown("---")

# تابع اجرای مستقیم فایل‌های پایتون
def run_script(script_name, label):
    try:
        st.info(f"⏳ در حال اجرای {label} ...")
        file_path = f"./{script_name}"
        spec = importlib.util.spec_from_file_location("module.name", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        st.success(f"✅ {label} با موفقیت اجرا شد.")
    except Exception as e:
        st.error(f"❌ خطا در اجرای {label}")
        st.exception(e)

# دکمه‌های اجرای هر مرحله
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 دریافت داده از صرافی"):
        run_script("fetch_data.py", "دریافت داده")

    if st.button("📈 تولید سیگنال‌ها"):
        run_script("final-signal.py", "تولید سیگنال")

with col2:
    if st.button("📊 محاسبه اندیکاتورها"):
        run_script("analyes.py", "محاسبه اندیکاتورها")

    if st.button("💰 تحلیل معاملات"):
        run_script("result.py", "تحلیل معاملات")

# اجرای کامل مراحل به‌ترتیب
if st.button("🔄 اجرای همه مراحل"):
    steps = [
        ("fetch_data.py", "دریافت داده"),
        ("analyes.py", "محاسبه اندیکاتورها"),
        ("final-signal.py", "تولید سیگنال"),
        ("result.py", "تحلیل معاملات"),
    ]
    for script, label in steps:
        run_script(script, label)

st.markdown("---")

# نمایش جدول سیگنال‌ها
if os.path.exists("btc_signals_15m.csv"):
    st.subheader("📋 جدول سیگنال‌های اخیر")
    df = pd.read_csv("btc_signals_15m.csv")
    st.dataframe(df.tail(20))

# رسم نمودار رشد سرمایه
if os.path.exists("btc_signals_15m.csv"):
    df = pd.read_csv("btc_signals_15m.csv")
    if "signal" in df.columns and "close" in df.columns:
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
        equity = [1000]
        for pnl in trades:
            equity.append(equity[-1] + pnl)
        st.subheader("📊 نمودار رشد سرمایه")
        fig, ax = plt.subplots()
        ax.plot(equity, marker="o")
        ax.set_title("نمودار رشد سرمایه")
        ax.set_xlabel("تعداد معاملات")
        ax.set_ylabel("سرمایه (دلار)")
        ax.grid(True)
        st.pyplot(fig)
