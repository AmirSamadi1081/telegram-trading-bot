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
    # آخرین کندل بسته شده
    # =====================================================
    def closed_df(self, df):

        if df is None or len(df) < 50:
            return None

        result = df.iloc[:-1].copy()

        if len(result) < 50:
            return None

        return result

    # =====================================================
    # روند BTC
    # =====================================================
    def btc_trend(self, btc_df):

        btc_df = self.closed_df(btc_df)

        if btc_df is None:
            return None

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

    # =====================================================
    # Trendline Breakout
    # =====================================================
    def trendline_breakout(self, df):

        if df is None or len(df) < self.swing_length * 3:
            return False, False

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

            current_ph = ph.iloc[i]
            current_pl = pl.iloc[i]
            current_slope = slope.iloc[i]

            if pd.isna(current_slope):
                continue

            # -----------------------------
            # Upper trendline
            # -----------------------------
            if not pd.isna(current_ph):

                upper = float(current_ph)

            elif not pd.isna(upper):

                upper -= float(current_slope)

            # -----------------------------
            # Lower trendline
            # -----------------------------
            if not pd.isna(current_pl):

                lower = float(current_pl)

            elif not pd.isna(lower):

                lower += float(current_slope)

            close = float(df["close"].iloc[i])

            # -----------------------------
            # Breakout
            # -----------------------------
            if not pd.isna(upper):

                if close > upper:
                    upper_break = True

            if not pd.isna(lower):

                if close < lower:
                    lower_break = True

        return upper_break, lower_break

    # =====================================================
    # Momentum / DMO
    # =====================================================
    def momentum_filter(self, df):

        if df is None or len(df) < self.dmo_length + 10:
            return None

        try:
            d = dmo(df, self.dmo_length)
        except Exception:
            return None

        if d is None or len(d) == 0:
            return None

        last = d.iloc[-1]

        if pd.isna(last):
            return None

        last = float(last)

        if last > self.threshold:
            return "BULLISH"

        if last < -self.threshold:
            return "BEARISH"

        return None

    # =====================================================
    # قدرت حرکت
    # =====================================================
    def momentum_strength(self, df):

        if df is None or len(df) < self.dmo_length + 10:
            return 0.0

        try:
            d = dmo(df, self.dmo_length)
        except Exception:
            return 0.0

        if d is None or len(d) < 2:
            return 0.0

        value = d.iloc[-1]

        if pd.isna(value):
            return 0.0

        return abs(float(value))

    # =====================================================
    # بررسی حجم
    # =====================================================
    def volume_filter(self, df):

        if df is None or len(df) < 25:
            return None

        if "volume" not in df.columns:
            return True

        volume = pd.to_numeric(
            df["volume"],
            errors="coerce"
        )

        if volume.isna().all():
            return True

        current_volume = volume.iloc[-1]

        average_volume = volume.iloc[-21:-1].mean()

        if pd.isna(current_volume) or pd.isna(average_volume):
            return True

        # حجم خیلی پایین = سیگنال ضعیف
        if current_volume < average_volume * 0.5:
            return False

        return True

    # =====================================================
    # Main Signal
    # =====================================================
    def generate_signal(
        self,
        df,
        btc_df=None
    ):

        # -------------------------------------------------
        # حذف کندل در حال تشکیل
        # -------------------------------------------------
        df = self.closed_df(df)

        if df is None:
            return None

        # -------------------------------------------------
        # Breakout
        # -------------------------------------------------
        upper_break, lower_break = self.trendline_breakout(df)

        # -------------------------------------------------
        # Momentum
        # -------------------------------------------------
        momentum = self.momentum_filter(df)

        if momentum is None:
            return None

        # -------------------------------------------------
        # Momentum Strength
        # -------------------------------------------------
        strength = self.momentum_strength(df)

        if strength < self.threshold:
            return None

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------
        volume_ok = self.volume_filter(df)

        if volume_ok is False:
            return None

        # -------------------------------------------------
        # BTC Filter
        # -------------------------------------------------
        btc_trend = None

        if btc_df is not None:
            btc_trend = self.btc_trend(btc_df)

        # -------------------------------------------------
        # قیمت آخرین کندل بسته شده
        # -------------------------------------------------
        price = float(df["close"].iloc[-1])

        # =================================================
        # BUY
        # =================================================
        if upper_break and momentum == "BULLISH":

            # اگر BTC اطلاعات معتبر دارد،
            # برای BUY بهتر است BTC صعودی باشد.
            if btc_trend is not None:

                if btc_trend != "BULLISH":
                    return None

            return {
                "signal": "BUY",
                "price": price
            }

        # =================================================
        # SELL
        # =================================================
        if lower_break and momentum == "BEARISH":

            # برای SELL لازم نیست BTC حتماً نزولی باشد،
            # ولی اگر BTC صعودی شدید باشد، سیگنال حذف می‌شود.
            if btc_trend == "BULLISH":

                btc_df_closed = self.closed_df(btc_df)

                if btc_df_closed is not None:

                    btc_ema = ema(
                        btc_df_closed["close"],
                        50
                    )

                    if not pd.isna(btc_ema.iloc[-1]):

                        btc_close = float(
                            btc_df_closed["close"].iloc[-1]
                        )

                        btc_ema_value = float(
                            btc_ema.iloc[-1]
                        )

                        # BTC بالاتر از EMA50 است،
                        # بنابراین SELL ضعیف‌تر است.
                        if btc_close > btc_ema_value * 1.01:
                            return None

            return {
                "signal": "SELL",
                "price": price
            }

        return None
