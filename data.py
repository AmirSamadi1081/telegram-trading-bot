import requests
import pandas as pd

BASE_URL = "https://www.okx.com"

BAR_MAP = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",
    "4h": "4H"
}

def get_klines(symbol="BTCUSDT", interval="15m", limit=300):
    inst_id = symbol.replace("USDT", "-USDT-SWAP")
    bar = BAR_MAP[interval]

    url = f"{BASE_URL}/api/v5/market/candles"
    params = {
        "instId": inst_id,
        "bar": bar,
        "limit": limit
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    data = r.json()

    if data.get("code") != "0":
        raise Exception(f"OKX API Error: {data.get('msg')}")

    candles = data["data"]

    df = pd.DataFrame(candles, columns=[
        "open_time", "open", "high", "low", "close",
        "volume", "volCcy", "volCcyQuote", "confirm"
    ])

    df[["open", "high", "low", "close", "volume"]] = (
        df[["open", "high", "low", "close", "volume"]].astype(float)
    )

    df["open_time"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms")

    df = df.iloc[::-1].reset_index(drop=True)

    return df
