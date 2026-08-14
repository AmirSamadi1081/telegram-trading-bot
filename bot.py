import time
from scanner import run_scanner
from config import SCAN_INTERVAL

print("SUMO Scanner Started...")

while True:
    try:
        run_scanner()
    except Exception as e:
        print(f"Scanner Error: {e}")

    time.sleep(SCAN_INTERVAL)