import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from data import get_klines
from strategy import SumoStrategy
from telegram_sender import TelegramSender
from config import SYMBOLS, TIMEFRAMES, KLINE_LIMIT


# =====================================================
# Objects
# =====================================================

strategy = SumoStrategy()
telegram = TelegramSender()


# =====================================================
# State
# =====================================================

STATE_FILE = "state.json"

state_lock = threading.Lock()
btc_lock = threading.Lock()


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

    except Exception as e:
        print(f"State load error: {e}")

    return {}


def save_state():
    try:
        with state_lock:
            temp_file = STATE_FILE + ".tmp"

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    state,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            os.replace(
                temp_file,
                STATE_FILE
            )

    except Exception as e:
        print(f"State save error: {e}")


state = load_state()


# =====================================================
# BTC Cache
# =====================================================

btc_cache = {}


def load_btc_cache():

    print("Loading BTC cache...")

    for timeframe in TIMEFRAMES:

        try:

            btc_df = get_klines(
                "BTCUSDT",
                timeframe,
                KLINE_LIMIT
            )

            if btc_df is not None and len(btc_df) > 0:

                with btc_lock:
                    btc_cache[timeframe] = btc_df

                print(
                    f"BTC {timeframe} cache loaded"
                )

            else:

                print(
                    f"BTC {timeframe} returned empty data"
                )

        except Exception as e:

            print(
                f"BTC {timeframe} error: {e}"
            )

        # جلوگیری از فشار روی API
        time.sleep(0.5)


# =====================================================
# Get BTC
# =====================================================

def get_cached_btc(timeframe):

    with btc_lock:
        return btc_cache.get(timeframe)


# =====================================================
# Scan Symbol
# =====================================================

def scan_symbol(symbol, timeframe):

    try:

        # -------------------------------------------------
        # دریافت کندل نماد
        # -------------------------------------------------

        df = get_klines(
            symbol,
            timeframe,
            KLINE_LIMIT
        )

        if df is None or len(df) < 60:

            print(
                f"SCAN {symbol} {timeframe} -> "
                f"NOT ENOUGH DATA"
            )

            return

        # -------------------------------------------------
        # BTC Cache
        # -------------------------------------------------

        btc_df = get_cached_btc(
            timeframe
        )

        # -------------------------------------------------
        # Generate Signal
        # -------------------------------------------------

        signal = strategy.generate_signal(
            df,
            btc_df
        )

        print(
            f"SCAN {symbol} {timeframe} -> {signal}"
        )

        # -------------------------------------------------
        # No Signal
        # -------------------------------------------------

        if signal is None:
            return

        current_signal = signal["signal"]

        price = signal["price"]

        # -------------------------------------------------
        # State Key
        # -------------------------------------------------

        key = f"{symbol}_{timeframe}"

        with state_lock:

            previous_signal = state.get(key)

            # سیگنال دقیقاً مشابه قبلی
            # دوباره ارسال نشود
            if previous_signal == current_signal:

                print(
                    f"DUPLICATE {symbol} "
                    f"{timeframe} -> "
                    f"{current_signal}"
                )

                return

            # -------------------------------------------------
            # ثبت State
            # -------------------------------------------------

            state[key] = current_signal

        # -------------------------------------------------
        # Telegram
        # -------------------------------------------------

        try:

            telegram.send_signal(
                symbol=symbol,
                timeframe=timeframe,
                signal=current_signal,
                price=price
            )

        except Exception as e:

            # اگر تلگرام شکست خورد،
            # state را به حالت قبلی برگردان
            with state_lock:

                if previous_signal is None:
                    state.pop(key, None)

                else:
                    state[key] = previous_signal

            print(
                f"Telegram error "
                f"{symbol} {timeframe}: {e}"
            )

            return

        # -------------------------------------------------
        # Save State
        # -------------------------------------------------

        save_state()

        print(
            f"NEW SIGNAL "
            f"{symbol} {timeframe} - "
            f"{signal}"
        )

    except Exception as e:

        print(
            f"Error {symbol} "
            f"{timeframe}: {e}"
        )


# =====================================================
# Scanner
# =====================================================

def run_scanner():

    print("================================")
    print("Starting new scan...")
    print("================================")

    # -------------------------------------------------
    # اول BTC Cache
    # -------------------------------------------------

    load_btc_cache()

    # اگر BTC هیچ داده‌ای نگرفت
    if not btc_cache:

        print(
            "WARNING: BTC cache is empty."
        )

        return

    # -------------------------------------------------
    # Tasks
    # -------------------------------------------------

    tasks = []

    for symbol in SYMBOLS:

        # BTC خودش قبلاً دریافت شده
        # پس دوباره برای BTC درخواست نمی‌فرستیم
        if symbol == "BTCUSDT":
            continue

        for timeframe in TIMEFRAMES:

            tasks.append(
                (
                    symbol,
                    timeframe
                )
            )

    # -------------------------------------------------
    # محدود کردن Threadها
    # -------------------------------------------------

    max_workers = 2

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = []

        for symbol, timeframe in tasks:

            futures.append(
                executor.submit(
                    scan_symbol,
                    symbol,
                    timeframe
                )
            )

            # فاصله بسیار کوتاه بین درخواست‌ها
            # برای کاهش احتمال 429
            time.sleep(0.15)

        # -------------------------------------------------
        # دریافت نتیجه Taskها
        # -------------------------------------------------

        for future in as_completed(futures):

            try:
                future.result()

            except Exception as e:

                print(
                    f"Worker error: {e}"
                )

    print("================================")
    print("Scan completed.")
    print("================================")


# =====================================================
# Direct Run
# =====================================================

if __name__ == "__main__":
    run_scanner()
