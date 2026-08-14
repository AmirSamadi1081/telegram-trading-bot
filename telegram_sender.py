import requests
from config import TOKEN, CHAT_ID


class TelegramSender:

    def __init__(self):
        self.url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    def send_signal(
        self,
        symbol,
        timeframe,
        signal,
        price
    ):

        emoji = "🟢" if signal == "BUY" else "🔴"

        text = f"""
{emoji} SUMO SIGNAL

Coin: {symbol}
Timeframe: {timeframe}
Signal: {signal}
Price: {price}
        """

        try:

            requests.post(
                self.url,
                data={
                    "chat_id": CHAT_ID,
                    "text": text
                },
                timeout=10
            )

        except Exception as e:
            print(f"Telegram Error: {e}")