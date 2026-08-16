import time
import requests
import pandas as pd

BASE_URL = "https://www.okx.com"

BAR_MAP = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",
    "4h": "4H"
}

# -----------------------------------------------------
# تبدیل نماد
# -----------------------------------------------------

def get_inst_id(symbol):
    return symbol.replace("USDT", "-USDT-SWAP")


# -----------------------------------------------------
# دریافت کندل‌ها از OKX
# -----------------------------------------------------

def get_klines(symbol="BTCUSDT", interval="15m", limit=200):

    if interval not in BAR_MAP:
        raise ValueError(f"Unsupported timeframe: {interval}")

    inst_id = get_inst_id(symbol)
    bar = BAR_MAP[interval]

    url = f"{BASE_URL}/api/v5/market/candles"

    params = {
        "instId": inst_id,
        "bar": bar,
        "limit": min(int(limit), 200)
    }

    # -------------------------------------------------
    # تلاش مجدد برای خطای 429
    # -------------------------------------------------

    max_retries = 4

    for attempt in range(max_retries):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            # Rate Limit
            if response.status_code == 429:

                wait_time = 2 ** attempt

                print(
                    f"OKX rate limit: "
                    f"{symbol} {interval} "
                    f"-> retry in {wait_time}s"
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()

            data = response.json()

            if data.get("code") != "0":
                raise Exception(
                    f"OKX API Error: {data.get('msg')}"
                )

            candles = data.get("data", [])

            if not candles:
                raise Exception(
                    f"No candle data for {symbol} {interval}"
                )

            # -------------------------------------------------
            # تبدیل DataFrame
            # -------------------------------------------------

            df = pd.DataFrame(
                candles,
                columns=[
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
            )

            numeric_columns = [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

            df[numeric_columns] = (
                df[numeric_columns]
                .apply(pd.to_numeric, errors="coerce")
            )

            df["open_time"] = pd.to_datetime(
                df["open_time"].astype("int64"),
                unit="ms"
            )

            # OKX داده‌ها را از جدید به قدیم می‌دهد
            # ما آن را به قدیم -> جدید تبدیل می‌کنیم

            df = (
                df.iloc[::-1]
                .reset_index(drop=True)
            )

            # حذف داده‌های خراب
            df = df.dropna(
                subset=[
                    "open",
                    "high",
                    "low",
                    "close"
                ]
            ).reset_index(drop=True)

            return df

        except requests.RequestException as e:

            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt

            print(
                f"Request error "
                f"{symbol} {interval}: {e} "
                f"-> retry in {wait_time}s"
            )

            time.sleep(wait_time)

    raise Exception(
        f"Failed to fetch {symbol} {interval}"
    )
