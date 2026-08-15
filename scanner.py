from concurrent.futures import ThreadPoolExecutor
from data import get_klines
from strategy import SumoStrategy
from telegram_sender import TelegramSender
from config import SYMBOLS, TIMEFRAMES
import json
import os

strategy = SumoStrategy()
telegram = TelegramSender()

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


state = load_state()


def scan_symbol(symbol, timeframe):
    try:
        df = get_klines(symbol, timeframe, 200)
        btc_df = get_klines("BTCUSDT", timeframe, 200)

        signal = strategy.generate_signal(df, btc_df)

        if signal:
            key = f"{symbol}_{timeframe}"
            current_signal = signal["signal"]
            previous_signal = state.get(key)

            # فقط اگر سیگنال تغییر کرده باشد
            if previous_signal != current_signal:
                telegram.send_signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    signal=current_signal,
                    price=signal["price"]
                )

                state[key] = current_signal
                save_state(state)

                print(f"NEW SIGNAL {symbol} {timeframe} - {signal}")

    except Exception as e:
        print(f"Error {symbol} {timeframe}: {e}")


def run_scanner():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []

        for symbol in SYMBOLS:
            for timeframe in TIMEFRAMES:
                futures.append(
                    executor.submit(
                        scan_symbol,
                        symbol,
                        timeframe
                    )
                )

        for future in futures:
            future.result()


if __name__ == "__main__":
    run_scanner()
