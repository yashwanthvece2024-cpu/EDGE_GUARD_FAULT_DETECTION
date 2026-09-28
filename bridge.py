import serial
import json
import time
import os
import threading
from config import SERIAL_PORT, BAUD_RATE

TELEMETRY_FILE = "data/telemetry.jsonl"
COMMAND_FILE = "data/command.txt"

def setup_files():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()
    if not os.path.exists(COMMAND_FILE):
        open(COMMAND_FILE, 'w').close()

def command_listener(ser):
    while True:
        try:
            if os.path.exists(COMMAND_FILE) and os.path.getsize(COMMAND_FILE) > 0:
                with open(COMMAND_FILE, "r+") as f:
                    cmd = f.read().strip()
                    if cmd == "ON":
                        ser.write(b'1\n')
                        print("-> Sent: MOTOR ON")
                    elif cmd in ["OFF", "STOP"]:
                        ser.write(b'0\n')
                        print("-> Sent: MOTOR OFF/STOP")
                    f.seek(0)
                    f.truncate()
        except Exception as e:
            pass
        time.sleep(0.5)

def main():
    setup_files()
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser.reset_input_buffer()
        print(f"Connected to EdgeGuard hardware on {SERIAL_PORT} at {BAUD_RATE} baud.")
        
        cmd_thread = threading.Thread(target=command_listener, args=(ser,), daemon=True)
        cmd_thread.start()
        
    except serial.SerialException:
        print(f"ERROR: Could not open {SERIAL_PORT}. Ensure ESP32 is connected and not locked.")
        return

    print("Listening for telemetry...")
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        data = json.loads(line)
                        with open(TELEMETRY_FILE, 'a') as f:
                            f.write(json.dumps(data) + "\n")
                    except json.JSONDecodeError:
                        pass
            time.sleep(0.01)
        except KeyboardInterrupt:
            print("\nShutting down bridge.")
            ser.close()
            break

if __name__ == "__main__":
    main()