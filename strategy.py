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

    # =========================================================
    # آخرین کندل بسته شده
    # =========================================================
    def last_closed(self, df):
        if df is None or len(df) < 3:
            return df

        return df.iloc[:-1].copy()

    # =========================================================
    # BTC Trend Filter
    # =========================================================
    def btc_trend(self, btc_df):

        if btc_df is None or len(btc_df) < 60:
            return None

        btc_df = self.last_closed(btc_df)

        ema50 = ema(btc_df["close"], 50)

        if pd.isna(ema50.iloc[-1]):
            return None

        close = float(btc_df["close"].iloc[-1])
        ema_value = float(ema50.iloc[-1])

        if close > ema_value:
            return "BULLISH"

        if close < ema_value:
            return "BEARISH"

        return None

    # =========================================================
    # Trendline Breakout
    # =========================================================
    def trendline_breakout(self, df):

        if df is None or len(df) < self.swing_length * 3:
            return False, False

        df = self.last_closed(df)

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

            # -------------------------
            # Upper trendline
            # -------------------------
            if not np.isnan(ph.iloc[i]):
                upper = ph.iloc[i]

            elif not np.isnan(upper):
                if not np.isnan(slope.iloc[i]):
                    upper -= slope.iloc[i]

            # -------------------------
            # Lower trendline
            # -------------------------
            if not np.isnan(pl.iloc[i]):
                lower = pl.iloc[i]

            elif not np.isnan(lower):
                if not np.isnan(slope.iloc[i]):
                    lower += slope.iloc[i]

            # -------------------------
            # Breakouts
            # -------------------------
            if not np.isnan(upper):

                if df["close"].iloc[i] > upper:
                    upper_break = True

            if not np.isnan(lower):

                if df["close"].iloc[i] < lower:
                    lower_break = True

        return upper_break, lower_break

    # =========================================================
    # DMO Momentum Filter
    # =========================================================
    def momentum_filter(self, df):

        if df is None or len(df) < self.dmo_length + 5:
            return None

        df = self.last_closed(df)

        d = dmo(
            df,
            self.dmo_length
        )

        if d is None or len(d) == 0:
            return None

        last = d.iloc[-1]

        if pd.isna(last):
            return None

        if last > self.threshold:
            return "BULLISH"

        if last < -self.threshold:
            return "BEARISH"

        return None

    # =========================================================
    # Main Signal
    # =========================================================
    def generate_signal(
        self,
        df,
        btc_df=None
    ):

        if df is None or len(df) < 50:
            return None

        # فقط کندل بسته شده
        closed_df = self.last_closed(df)

        if closed_df is None or len(closed_df) < 50:
            return None

        # -------------------------
        # Trendline
        # -------------------------
        upper_break, lower_break = self.trendline_breakout(
            closed_df
        )

        # -------------------------
        # Momentum
        # -------------------------
        momentum = self.momentum_filter(
            closed_df
        )

        # -------------------------
        # BTC Filter
        # -------------------------
        btc_state = "BULLISH"

        if btc_df is not None:

            btc_state = self.btc_trend(
                btc_df
            )

            if btc_state is None:
                return None

        # -------------------------
        # Current price
        # -------------------------
        price = float(
            closed_df["close"].iloc[-1]
        )

        # =====================================================
        # BUY
        # =====================================================
        #
        # شکست صعودی
        # مومنتوم صعودی
        # BTC صعودی
        #
        # =====================================================

        if (
            upper_break
            and momentum == "BULLISH"
            and btc_state == "BULLISH"
        ):

            return {
                "signal": "BUY",
                "price": price
            }

        # =====================================================
        # SELL
        # =====================================================
        #
        # شکست نزولی
        # مومنتوم نزولی
        #
        # برای SELL فیلتر BTC اجباری نیست
        # =====================================================

        if (
            lower_break
            and momentum == "BEARISH"
        ):

            return {
                "signal": "SELL",
                "price": price
            }

        return None
