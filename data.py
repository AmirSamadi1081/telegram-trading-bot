import requests
import pandas as pd

BASE_URL = "https://api.binance.com"


def get_klines(symbol="BTCUSDT", interval="15m", limit=500):
    url = f"{BASE_URL}/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(
        url,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    r.raise_for_status()

    data = r.json()

    if not data:
        raise ValueError(f"No kline data returned for {symbol} {interval}")

    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore"
        ]
    )

    df[
        ["open", "high", "low", "close", "volume"]
    ] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    df["open_time"] = pd.to_datetime(
        df["open_time"],
        unit="ms"
    )

    df["close_time"] = pd.to_datetime(
        df["close_time"],
        unit="ms"
    )

    return df
