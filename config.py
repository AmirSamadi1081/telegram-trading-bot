import os

# =====================================================
# Telegram
# =====================================================

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# =====================================================
# OKX
# =====================================================

BASE_URL = "https://www.okx.com"


# =====================================================
# Timeframes
# =====================================================

TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h"
]


# =====================================================
# Symbols
# =====================================================

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


# =====================================================
# Scanner
# =====================================================

SCAN_INTERVAL = 180
KLINE_LIMIT = 200
