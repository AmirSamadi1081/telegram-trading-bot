import requests
import pandas as pd

BASE_URL = "https://api.bybit.com"


def get_klines(symbol="BTCUSDT", interval="15m", limit=500):

    interval_map = {
        "5m": "5",
        "15m": "15",
        "1h": "60",
        "4h": "240"
    }

    if interval not in interval_map:
        raise ValueError(f"Unsupported interval: {interval}")

    url = f"{BASE_URL}/v5/market/kline"

    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval_map[interval],
        "limit": limit
    }

    response = requests.get(
        url,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    result = response.json()

    if result.get("retCode") != 0:
        raise RuntimeError(
            f"Bybit API error: {result.get('retMsg')}"
        )

    data = result["result"]["list"]

    if not data:
        raise ValueError(
            f"No kline data returned for {symbol} {interval}"
        )

    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]
    )

    df[
        ["open", "high", "low", "close", "volume", "turnover"]
    ] = df[
        ["open", "high", "low", "close", "volume", "turnover"]
    ].astype(float)

    df["open_time"] = pd.to_datetime(
        df["open_time"].astype("int64"),
        unit="ms"
    )

    # Bybit returns newest candle first.
    # Reverse it so the DataFrame is oldest -> newest.
    df = df.iloc[::-1].reset_index(drop=True)

    return df
