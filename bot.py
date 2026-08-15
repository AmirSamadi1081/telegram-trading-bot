import time
from scanner import run_scanner

print("SUMO Scanner Started...")

while True:
    try:
        run_scanner()
    except Exception as e:
        print(f"Scanner error: {e}")

    # هر 3 دقیقه یک بار اسکن
    time.sleep(180)
