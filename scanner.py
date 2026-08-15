from concurrent.futures import ThreadPoolExecutor
from data import get_klines
from strategy import SumoStrategy
from telegram_sender import TelegramSender
from config import SYMBOLS, TIMEFRAMES

strategy = SumoStrategy()
telegram = TelegramSender()


def scan_symbol(symbol, timeframe):
    try:
        df = get_klines(symbol, timeframe, 500)
        btc_df = get_klines("BTCUSDT", timeframe, 500)

        signal = strategy.generate_signal(df, btc_df)

        if signal:
            telegram.send_signal(
                symbol=symbol,
                timeframe=timeframe,
                signal=signal["signal"],
                price=signal["price"]
            )

            print(f"{symbol} {timeframe} - {signal}")

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
