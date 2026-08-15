import os

# ==============================
# Telegram
# ==============================
TOKEN = os.environ.get("8865723060:AAFjs7IkbZjw1xqCK8uqWUYKwkS95cBt8Rs")
CHAT_ID = os.environ.get("7333396434")

# ==============================
# Binance
# ==============================
BASE_URL = "https://fapi.binance.com"

# ==============================
# Timeframes
# ==============================
TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h"
]

# ==============================
# Symbols (Initial Watchlist)
# ==============================
SYMBOLS = [
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
]

# ==============================
# Scanner
# ==============================
SCAN_INTERVAL = 60        # seconds
KLINE_LIMIT = 200         # candles
