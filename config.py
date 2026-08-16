import os


# ==============================
# Telegram
# ==============================

TOKEN = os.environ.get("8865723060:AAFjs7IkbZjw1xqCK8uqWUYKwkS95cBt8Rs", "")
CHAT_ID = os.environ.get("7333396434", "")


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
# Symbols
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

SCAN_INTERVAL = 180
KLINE_LIMIT = 200
