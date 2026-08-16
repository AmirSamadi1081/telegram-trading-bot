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

        text = (
            f"{emoji} SUMO SIGNAL\n\n"
            f"Coin: {symbol}\n"
            f"Timeframe: {timeframe}\n"
            f"Signal: {signal}\n"
            f"Price: {price}"
        )

        try:

            response = requests.post(
                self.url,
                data={
                    "chat_id": CHAT_ID,
                    "text": text
                },
                timeout=15
            )

            print(
                f"Telegram response: "
                f"{response.status_code} -> {response.text}"
            )

            if response.status_code != 200:
                print(
                    f"Telegram HTTP Error: "
                    f"{response.status_code}"
                )
                return False

            result = response.json()

            if not result.get("ok"):
                print(
                    f"Telegram API Error: "
                    f"{result}"
                )
                return False

            print(
                f"Telegram signal sent successfully: "
                f"{symbol} {timeframe} {signal}"
            )

            return True

        except requests.RequestException as e:

            print(
                f"Telegram Connection Error: {e}"
            )

            return False

        except Exception as e:

            print(
                f"Telegram Error: {e}"
            )

            return False
