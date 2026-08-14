import pandas as pd
import numpy as np


# =====================================================
# EMA
# =====================================================
def ema(series: pd.Series, length: int):
    return series.ewm(span=length, adjust=False).mean()


# =====================================================
# ATR
# =====================================================
def atr(df: pd.DataFrame, length: int):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    prev_close = close.shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(length).mean()


# =====================================================
# DMO (same logic as Pine)
# =====================================================
def dmo(df: pd.DataFrame, length=14, smoothing=False):
    momentum = df["close"] - df["close"].shift(length)

    range1 = (
        df["high"].rolling(length).max()
        - df["low"].rolling(length).min()
    )

    dmo_val = momentum / range1

    if smoothing:
        dmo_val = dmo_val.rolling(8).mean()

    return dmo_val


# =====================================================
# Pivot High / Pivot Low
# Similar to ta.pivothigh() and ta.pivotlow()
# =====================================================
def pivot_high(series: pd.Series, left: int, right: int):
    result = [np.nan] * len(series)

    for i in range(left, len(series) - right):
        window = series.iloc[i - left:i + right + 1]
        if series.iloc[i] == window.max():
            result[i] = series.iloc[i]

    return pd.Series(result, index=series.index)


def pivot_low(series: pd.Series, left: int, right: int):
    result = [np.nan] * len(series)

    for i in range(left, len(series) - right):
        window = series.iloc[i - left:i + right + 1]
        if series.iloc[i] == window.min():
            result[i] = series.iloc[i]

    return pd.Series(result, index=series.index)


# =====================================================
# Trendline Slope (ATR method)
# =====================================================
def trendline_slope(df: pd.DataFrame, length: int, mult: float = 1.0):
    return atr(df, length) / length * mult