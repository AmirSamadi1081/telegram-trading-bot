import os
import requests

API_KEY = os.getenv("abf78a95-1ad0-4062-81e9-2d8e54d180ef")

if not API_KEY:
    print("ERROR: COINAPI_KEY is not set")
    raise SystemExit(1)

url = "https://rest.coinapi.io/v1/exchangerate/BTC/USD"

headers = {
    "X-CoinAPI-Key": API_KEY
}

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE:", response.text)

except Exception as e:
    print("CONNECTION ERROR:", repr(e))