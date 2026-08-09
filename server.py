from flask import Flask, request
import requests
import os

app = Flask(__name__)

TOKEN = "8865723060:AAFjs7IkbZjw1xqCK8uqWUYKwkS95cBt8Rs"
CHAT_ID = "7333396434"

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

@app.route("/signal", methods=["POST"])
def signal():
    data = request.json

    symbol = data.get("symbol", "Unknown")
    signal = data.get("signal", "Unknown")
    price = data.get("price", "Unknown")
    timeframe = data.get("timeframe", "Unknown")

    message = f"""🚨 سیگنال جدید

📌 نماد: {symbol}
⏰ تایم‌فریم: {timeframe}
📊 سیگنال: {signal}
💰 قیمت: {price}"""

    send_message(message)

    return {"status": "ok"}

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)