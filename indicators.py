import pandas as pd
import numpy as np

# =====================================================
# EMA
# =====================================================

def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

# =====================================================
# ATR
# =====================================================

def atr(df, length=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.rolling(length).mean()

# =====================================================
# DMO (Directional Momentum Oscillator)
# =====================================================

def dmo(df, length=14):
    up = df["high"].diff()
    down = -df["low"].diff()

    plus = np.where((up > down) & (up > 0), up, 0)
    minus = np.where((down > up) & (down > 0), down, 0)

    plus = pd.Series(plus, index=df.index)
    minus = pd.Series(minus, index=df.index)

    plus_ema = plus.ewm(span=length, adjust=False).mean()
    minus_ema = minus.ewm(span=length, adjust=False).mean()

    dmo_value = (plus_ema - minus_ema) / (
        plus_ema + minus_ema + 1e-9
    )

    return dmo_value

# =====================================================
# Super Bollinger
# =====================================================

def super_bollinger(df, length=20, mult=2.0):
    basis = df["close"].rolling(length).mean()
    dev = df["close"].rolling(length).std()

    upper = basis + mult * dev
    lower = basis - mult * dev

    trend = pd.Series(index=df.index, dtype="object")

    trend[df["close"] > upper] = "BULLISH"
    trend[df["close"] < lower] = "BEARISH"

    trend = trend.ffill()

    return trend

# =====================================================
# Pivot High
# =====================================================

def pivot_high(series, left=5, right=5):
    result = pd.Series(np.nan, index=series.index)

    for i in range(left, len(series) - right):

        window = series.iloc[
            i - left : i + right + 1
        ]

        if series.iloc[i] == window.max():
            result.iloc[i] = series.iloc[i]

    return result

# =====================================================
# Pivot Low
# =====================================================

def pivot_low(series, left=5, right=5):
    result = pd.Series(np.nan, index=series.index)

    for i in range(left, len(series) - right):

        window = series.iloc[
            i - left : i + right + 1
        ]

        if series.iloc[i] == window.min():
            result.iloc[i] = series.iloc[i]

    return result

# =====================================================
# Trendline Slope
# =====================================================

def trendline_slope(
    df,
    length=14,
    mult=1.0
):
    a = atr(df, length)

    slope = (a / length) * mult

    return slope.fillna(0)
