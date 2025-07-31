import pandas as pd
import numpy as np

# --- بارگذاری داده‌های خام ---
df_15m = pd.read_csv("btc_15m_raw.csv")
df_1h = pd.read_csv("btc_1h_raw.csv")

df_15m['timestamp'] = pd.to_datetime(df_15m['timestamp'])
df_1h['timestamp'] = pd.to_datetime(df_1h['timestamp'])

# --- اندیکاتورهای تایم‌فریم 15m ---
df = df_15m.copy()

# EMA
df['ema_9'] = df['close'].ewm(span=9).mean()
df['ema_21'] = df['close'].ewm(span=21).mean()

# RSI
delta = df['close'].diff()
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)
avg_gain = pd.Series(gain).rolling(window=14).mean()
avg_loss = pd.Series(loss).rolling(window=14).mean()
rs = avg_gain / avg_loss
df['rsi_14'] = 100 - (100 / (1 + rs))

# MACD
ema12 = df['close'].ewm(span=12).mean()
ema26 = df['close'].ewm(span=26).mean()
df['macd'] = ema12 - ema26
df['macd_signal'] = df['macd'].ewm(span=9).mean()

# Bollinger Bands
df['bb_mid'] = df['close'].rolling(window=20).mean()
df['bb_std'] = df['close'].rolling(window=20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']

# ATR
tr1 = df['high'] - df['low']
tr2 = abs(df['high'] - df['close'].shift())
tr3 = abs(df['low'] - df['close'].shift())
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=14).mean()

# Momentum
df['momentum'] = df['close'] - df['close'].shift(4)

# OBV
obv = [0]
for i in range(1, len(df)):
    if df['close'][i] > df['close'][i - 1]:
        obv.append(obv[-1] + df['volume'][i])
    elif df['close'][i] < df['close'][i - 1]:
        obv.append(obv[-1] - df['volume'][i])
    else:
        obv.append(obv[-1])
df['obv'] = obv

# --- محاسبه EMA200 و ADX در 1h ---
df_1h['ema_200_1h'] = df_1h['close'].ewm(span=200).mean()

# ADX
up_move = df_1h['high'].diff()
down_move = df_1h['low'].diff() * -1
plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

tr1 = df_1h['high'] - df_1h['low']
tr2 = abs(df_1h['high'] - df_1h['close'].shift())
tr3 = abs(df_1h['low'] - df_1h['close'].shift())
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
atr = pd.Series(tr).rolling(window=14).mean()
plus_di = 100 * pd.Series(plus_dm).rolling(window=14).mean() / atr
minus_di = 100 * pd.Series(minus_dm).rolling(window=14).mean() / atr
dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
df_1h['adx_1h'] = dx.rolling(window=14).mean()

# --- ترکیب EMA200 و ADX 1h با داده 15m ---
df_1h_reduced = df_1h[['timestamp', 'ema_200_1h', 'adx_1h']]
df_final = pd.merge_asof(df.sort_values('timestamp'),
                         df_1h_reduced.sort_values('timestamp'),
                         on='timestamp',
                         direction='backward')

# --- ذخیره خروجی ---
df_final.to_csv("btc_15m_with_indicators.csv", index=False)
print("✅ اندیکاتورها برای 15m و 1h محاسبه و ترکیب شدند.")
