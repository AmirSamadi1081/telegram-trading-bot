import pandas as pd
import numpy as np

from indicators import (
    dmo,
    pivot_high,
    pivot_low,
    trendline_slope,
    ema
)


class SumoStrategy:

    def __init__(
        self,
        swing_length=14,
        slope_mult=1.0,
        dmo_length=14,
        threshold=0.3
    ):
        self.swing_length = swing_length
        self.slope_mult = slope_mult
        self.dmo_length = dmo_length
        self.threshold = threshold

    # =====================================================
    # BTC Trend Filter
    # =====================================================
    def btc_trend(self, btc_df):

        ema50 = ema(btc_df["close"], 50)

        if pd.isna(ema50.iloc[-1]):
            return True

        return btc_df["close"].iloc[-1] > ema50.iloc[-1]

    # =====================================================
    # Trendline Breakout Logic
    # =====================================================
    def trendline_breakout(self, df):

        ph = pivot_high(
            df["high"],
            self.swing_length,
            self.swing_length
        )

        pl = pivot_low(
            df["low"],
            self.swing_length,
            self.swing_length
        )

        slope = trendline_slope(
            df,
            self.swing_length,
            self.slope_mult
        )

        upper = np.nan
        lower = np.nan

        upper_break = False
        lower_break = False

        for i in range(len(df)):

            if not np.isnan(ph.iloc[i]):
                upper = ph.iloc[i]

            elif not np.isnan(upper):
                upper -= slope.iloc[i]

            if not np.isnan(pl.iloc[i]):
                lower = pl.iloc[i]

            elif not np.isnan(lower):
                lower += slope.iloc[i]

            if not np.isnan(upper):
                if df["close"].iloc[i] > upper:
                    upper_break = True

            if not np.isnan(lower):
                if df["close"].iloc[i] < lower:
                    lower_break = True

        return upper_break, lower_break

    # =====================================================
    # DMO Filter
    # =====================================================
    def momentum_filter(self, df):

        d = dmo(df, self.dmo_length)

        last = d.iloc[-1]

        if pd.isna(last):
            return None

        if last > self.threshold:
            return "BULLISH"

        if last < -self.threshold:
            return "BEARISH"

        return None

    # =====================================================
    # Main Signal
    # =====================================================
    def generate_signal(
        self,
        df,
        btc_df=None
    ):

        if len(df) < 100:
            return None

        upper_break, lower_break = self.trendline_breakout(df)

        momentum = self.momentum_filter(df)

        btc_ok = True

        if btc_df is not None:
            btc_ok = self.btc_trend(btc_df)

        if upper_break and momentum == "BULLISH" and btc_ok:

            return {
                "signal": "BUY",
                "price": float(df["close"].iloc[-1])
            }

        if lower_break and momentum == "BEARISH":

            return {
                "signal": "SELL",
                "price": float(df["close"].iloc[-1])
            }

        return None
