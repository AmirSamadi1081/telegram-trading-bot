import time
import random
import threading

import requests
import pandas as pd


# =====================================================
# OKX
# =====================================================

BASE_URL = "https://www.okx.com"

CANDLES_URL = (
    f"{BASE_URL}/api/v5/market/candles"
)


# =====================================================
# Timeframes
# =====================================================

BAR_MAP = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",
    "4h": "4H"
}


# =====================================================
# Session
# =====================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "SUMO-Trading-Scanner/1.0",
    "Accept": "application/json"
})


# =====================================================
# Request Lock
#
# باعث می‌شود چند Thread همزمان به OKX
# درخواست سنگین نفرستند.
# =====================================================

request_lock = threading.Lock()


# =====================================================
# آخرین زمان درخواست
# =====================================================

last_request_time = 0.0

MIN_REQUEST_INTERVAL = 0.35


# =====================================================
# نمادهای مجاز
# =====================================================

VALID_SYMBOLS = {
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "BNBUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "SUIUSDT",
    "TRXUSDT",
    "DOTUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "APTUSDT",
    "NEARUSDT",
    "ARBUSDT",
    "OPUSDT",
    "ATOMUSDT"
}


# =====================================================
# تبدیل Symbol به OKX Instrument ID
# =====================================================

def get_inst_id(symbol):

    symbol = str(symbol).upper().strip()

    if symbol not in VALID_SYMBOLS:
        raise ValueError(
            f"Unsupported symbol: {symbol}"
        )

    if not symbol.endswith("USDT"):
        raise ValueError(
            f"Invalid symbol format: {symbol}"
        )

    base = symbol[:-4]

    return f"{base}-USDT-SWAP"


# =====================================================
# Rate Limit Protection
# =====================================================

def wait_before_request():

    global last_request_time

    with request_lock:

        now = time.monotonic()

        elapsed = (
            now - last_request_time
        )

        if elapsed < MIN_REQUEST_INTERVAL:

            sleep_time = (
                MIN_REQUEST_INTERVAL
                - elapsed
            )

            time.sleep(sleep_time)

        last_request_time = time.monotonic()


# =====================================================
# دریافت کندل‌ها
# =====================================================

def get_klines(
    symbol="BTCUSDT",
    interval="15m",
    limit=200
):

    symbol = str(symbol).upper().strip()
    interval = str(interval).lower().strip()

    # -------------------------------------------------
    # بررسی تایم‌فریم
    # -------------------------------------------------

    if interval not in BAR_MAP:

        raise ValueError(
            f"Unsupported timeframe: {interval}"
        )

    # -------------------------------------------------
    # بررسی Symbol
    # -------------------------------------------------

    inst_id = get_inst_id(symbol)

    bar = BAR_MAP[interval]

    # -------------------------------------------------
    # Limit
    # -------------------------------------------------

    try:
        limit = int(limit)
    except Exception:

        limit = 200

    limit = max(
        50,
        min(limit, 200)
    )

    params = {
        "instId": inst_id,
        "bar": bar,
        "limit": limit
    }

    # -------------------------------------------------
    # Retry
    # -------------------------------------------------

    max_retries = 5

    for attempt in range(max_retries):

        try:

            # -----------------------------------------
            # Rate limit داخلی
            # -----------------------------------------

            wait_before_request()

            # -----------------------------------------
            # Request
            # -----------------------------------------

            response = session.get(
                CANDLES_URL,
                params=params,
                timeout=20
            )

            # -----------------------------------------
            # HTTP 429
            # -----------------------------------------

            if response.status_code == 429:

                retry_after = (
                    response.headers.get(
                        "Retry-After"
                    )
                )

                if retry_after:

                    try:
                        wait_time = float(
                            retry_after
                        )

                    except Exception:
                        wait_time = 5.0

                else:

                    wait_time = min(
                        2 ** attempt,
                        15
                    )

                # کمی random delay
                wait_time += random.uniform(
                    0.2,
                    0.8
                )

                print(
                    f"OKX 429 | "
                    f"{symbol} {interval} | "
                    f"retry in "
                    f"{wait_time:.1f}s"
                )

                time.sleep(wait_time)

                continue

            # -----------------------------------------
            # سایر HTTP errors
            # -----------------------------------------

            response.raise_for_status()

            # -----------------------------------------
            # JSON
            # -----------------------------------------

            data = response.json()

            code = str(
                data.get("code", "")
            )

            # -----------------------------------------
            # OKX API Error
            # -----------------------------------------

            if code != "0":

                message = data.get(
                    "msg",
                    "Unknown OKX error"
                )

                message_lower = str(
                    message
                ).lower()

                # -------------------------------------
                # Instrument ID نامعتبر
                # -------------------------------------

                if (
                    "instrument id" in message_lower
                    or "doesn't exist" in message_lower
                    or "does not exist" in message_lower
                ):

                    raise ValueError(
                        f"Invalid OKX instrument "
                        f"{inst_id}: {message}"
                    )

                # -------------------------------------
                # Rate limit از API
                # -------------------------------------

                if (
                    "too many" in message_lower
                    or "rate limit" in message_lower
                ):

                    wait_time = min(
                        2 ** attempt,
                        15
                    )

                    print(
                        f"OKX API rate limit | "
                        f"{symbol} {interval} | "
                        f"retry in "
                        f"{wait_time}s"
                    )

                    time.sleep(
                        wait_time
                    )

                    continue

                raise Exception(
                    f"OKX API Error: "
                    f"{message}"
                )

            # -----------------------------------------
            # Candles
            # -----------------------------------------

            candles = data.get(
                "data",
                []
            )

            if not candles:

                raise Exception(
                    f"No candle data for "
                    f"{symbol} {interval}"
                )

            # -----------------------------------------
            # DataFrame
            # -----------------------------------------

            columns = [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "volCcy",
                "volCcyQuote",
                "confirm"
            ]

            df = pd.DataFrame(
                candles,
                columns=columns
            )

            # -----------------------------------------
            # Numeric
            # -----------------------------------------

            numeric_columns = [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            for column in numeric_columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

            # -----------------------------------------
            # Timestamp
            # -----------------------------------------

            df["open_time"] = pd.to_datetime(
                pd.to_numeric(
                    df["open_time"],
                    errors="coerce"
                ),
                unit="ms",
                errors="coerce"
            )

            # -----------------------------------------
            # حذف داده خراب
            # -----------------------------------------

            df = df.dropna(
                subset=[
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close"
                ]
            )

            # -----------------------------------------
            # قدیمی → جدید
            # -----------------------------------------

            df = (
                df.iloc[::-1]
                .reset_index(drop=True)
            )

            # -----------------------------------------
            # حذف Duplicate
            # -----------------------------------------

            df = df.drop_duplicates(
                subset=["open_time"],
                keep="last"
            )

            df = (
                df.sort_values("open_time")
                .reset_index(drop=True)
            )

            # -----------------------------------------
            # بررسی نهایی
            # -----------------------------------------

            if len(df) < 50:

                raise Exception(
                    f"Not enough candles for "
                    f"{symbol} {interval}: "
                    f"{len(df)}"
                )

            return df

        # =================================================
        # Request Exception
        # =================================================

        except requests.RequestException as e:

            if attempt >= max_retries - 1:

                raise Exception(
                    f"Request failed for "
                    f"{symbol} {interval}: "
                    f"{e}"
                )

            wait_time = min(
                2 ** attempt,
                15
            )

            wait_time += random.uniform(
                0.2,
                0.8
            )

            print(
                f"Request error | "
                f"{symbol} {interval} | "
                f"{e} | "
                f"retry in "
                f"{wait_time:.1f}s"
            )

            time.sleep(
                wait_time
            )

        # =================================================
        # Instrument / API errors
        # =================================================

        except ValueError:
            raise

        except Exception as e:

            if attempt >= max_retries - 1:
                raise

            wait_time = min(
                2 ** attempt,
                10
            )

            print(
                f"OKX error | "
                f"{symbol} {interval} | "
                f"{e} | "
                f"retry in "
                f"{wait_time}s"
            )

            time.sleep(
                wait_time
            )

    raise Exception(
        f"Failed to fetch "
        f"{symbol} {interval}"
    )
