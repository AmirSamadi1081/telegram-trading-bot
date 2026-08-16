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

        if df is None:
            return None

        if len(df) < 60:
            return None

        # آخرین کندل OKX معمولاً در حال تشکیل است
        result = df.iloc[:-1].copy()

        if len(result) < 60:
            return None

        return result.reset_index(drop=True)

    # =====================================================
    # روند BTC
    # =====================================================

    def btc_trend(self, btc_df):

        btc_df = self.closed_df(btc_df)

        if btc_df is None:
            return None

        try:
            ema50 = ema(btc_df["close"], 50)
        except Exception:
            return None

        if len(ema50) == 0:
            return None

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
    # فقط شکست جدید آخرین کندل بررسی می‌شود
    # =====================================================

    def trendline_breakout(self, df):

        if df is None:
            return False, False

        minimum_length = self.swing_length * 3 + 10

        if len(df) < minimum_length:
            return False, False

        try:

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

        except Exception:
            return False, False

        upper = np.nan
        lower = np.nan

        upper_values = []
        lower_values = []

        # -------------------------------------------------
        # ساخت خطوط روند
        # -------------------------------------------------

        for i in range(len(df)):

            current_ph = ph.iloc[i]
            current_pl = pl.iloc[i]
            current_slope = slope.iloc[i]

            if pd.isna(current_slope):
                current_slope = 0.0

            current_slope = float(current_slope)

            # -----------------------------
            # Upper
            # -----------------------------

            if not pd.isna(current_ph):

                upper = float(current_ph)

            elif not pd.isna(upper):

                upper -= current_slope

            # -----------------------------
            # Lower
            # -----------------------------

            if not pd.isna(current_pl):

                lower = float(current_pl)

            elif not pd.isna(lower):

                lower += current_slope

            upper_values.append(upper)
            lower_values.append(lower)

        # -------------------------------------------------
        # حداقل دو کندل آخر لازم است
        # -------------------------------------------------

        if len(upper_values) < 2:
            return False, False

        last_close = float(df["close"].iloc[-1])
        previous_close = float(df["close"].iloc[-2])

        last_upper = upper_values[-1]
        previous_upper = upper_values[-2]

        last_lower = lower_values[-1]
        previous_lower = lower_values[-2]

        upper_break = False
        lower_break = False

        # -------------------------------------------------
        # BUY breakout
        # قیمت قبلاً زیر خط بوده
        # و در آخرین کندل از خط عبور کرده
        # -------------------------------------------------

        if (
            not pd.isna(previous_upper)
            and not pd.isna(last_upper)
        ):

            if (
                previous_close <= previous_upper
                and last_close > last_upper
            ):
                upper_break = True

        # -------------------------------------------------
        # SELL breakout
        # قیمت قبلاً بالای خط بوده
        # و در آخرین کندل زیر خط رفته
        # -------------------------------------------------

        if (
            not pd.isna(previous_lower)
            and not pd.isna(last_lower)
        ):

            if (
                previous_close >= previous_lower
                and last_close < last_lower
            ):
                lower_break = True

        return upper_break, lower_break

    # =====================================================
    # DMO
    # =====================================================

    def momentum_filter(self, df):

        if df is None:
            return None

        if len(df) < self.dmo_length + 15:
            return None

        try:

            d = dmo(
                df,
                self.dmo_length
            )

        except Exception:
            return None

        if d is None or len(d) < 2:
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
    # قدرت Momentum
    # =====================================================

    def momentum_strength(self, df):

        if df is None:
            return 0.0

        if len(df) < self.dmo_length + 15:
            return 0.0

        try:

            d = dmo(
                df,
                self.dmo_length
            )

        except Exception:
            return 0.0

        if d is None or len(d) < 2:
            return 0.0

        value = d.iloc[-1]

        if pd.isna(value):
            return 0.0

        return abs(float(value))

    # =====================================================
    # Volume Filter
    # =====================================================

    def volume_filter(self, df):

        if df is None:
            return False

        if len(df) < 25:
            return False

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

        if pd.isna(current_volume):
            return True

        if pd.isna(average_volume):
            return True

        # حجم بسیار پایین
        if current_volume < average_volume * 0.5:
            return False

        return True

    # =====================================================
    # بررسی کندل
    # =====================================================

    def candle_confirmation(self, df, signal):

        if df is None or len(df) < 3:
            return False

        current = df.iloc[-1]

        open_price = float(current["open"])
        close_price = float(current["close"])
        high = float(current["high"])
        low = float(current["low"])

        candle_range = high - low

        if candle_range <= 0:
            return False

        body = abs(close_price - open_price)

        body_ratio = body / candle_range

        # کندل بسیار ضعیف
        if body_ratio < 0.20:
            return False

        if signal == "BUY":

            if close_price <= open_price:
                return False

            return True

        if signal == "SELL":

            if close_price >= open_price:
                return False

            return True

        return False

    # =====================================================
    # Main Signal
    # =====================================================

    def generate_signal(
        self,
        df,
        btc_df=None
    ):

        # -------------------------------------------------
        # فقط کندل بسته شده
        # -------------------------------------------------

        df = self.closed_df(df)

        if df is None:
            return None

        # -------------------------------------------------
        # Breakout
        # -------------------------------------------------

        upper_break, lower_break = self.trendline_breakout(df)

        # اگر همزمان هر دو رخ دادند، سیگنال نده
        if upper_break and lower_break:
            return None

        if not upper_break and not lower_break:
            return None

        # -------------------------------------------------
        # Momentum
        # -------------------------------------------------

        momentum = self.momentum_filter(df)

        if momentum is None:
            return None

        # -------------------------------------------------
        # قدرت Momentum
        # -------------------------------------------------

        strength = self.momentum_strength(df)

        if strength < self.threshold:
            return None

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------

        volume_ok = self.volume_filter(df)

        if not volume_ok:
            return None

        # -------------------------------------------------
        # BTC Trend
        # -------------------------------------------------

        btc_trend = None

        if btc_df is not None:
            btc_trend = self.btc_trend(btc_df)

        # -------------------------------------------------
        # Price
        # -------------------------------------------------

        price = float(
            df["close"].iloc[-1]
        )

        # =================================================
        # BUY
        # =================================================

        if upper_break:

            # Momentum باید صعودی باشد
            if momentum != "BULLISH":
                return None

            # کندل تأیید
            if not self.candle_confirmation(
                df,
                "BUY"
            ):
                return None

            # اگر BTC اطلاعات معتبر دارد
            # بهتر است BTC هم صعودی باشد
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

        if lower_break:

            # Momentum باید نزولی باشد
            if momentum != "BEARISH":
                return None

            # کندل تأیید
            if not self.candle_confirmation(
                df,
                "SELL"
            ):
                return None

            # اگر BTC صعودی شدید است،
            # SELL را حذف می‌کنیم.
            if btc_trend == "BULLISH":

                btc_closed = self.closed_df(
                    btc_df
                )

                if btc_closed is not None:

                    try:

                        btc_ema = ema(
                            btc_closed["close"],
                            50
                        )

                        if not pd.isna(
                            btc_ema.iloc[-1]
                        ):

                            btc_close = float(
                                btc_closed["close"].iloc[-1]
                            )

                            btc_ema_value = float(
                                btc_ema.iloc[-1]
                            )

                            # BTC بیش از 1٪ بالاتر از EMA50
                            if btc_close > btc_ema_value * 1.01:
                                return None

                    except Exception:
                        pass

            return {
                "signal": "SELL",
                "price": price
            }

        return None
