import json
import time
import serial
import serial.tools.list_ports

from config import TELEMETRY_FILE, DEFAULT_SERIAL_BAUD


def find_serial_ports():

    ports = serial.tools.list_ports.comports()

    return [port.device for port in ports]


def save_record(record):

    with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def run(port):

    print()
    print("=" * 50)
    print("EDGEGUARD HARDWARE BRIDGE")
    print("=" * 50)
    print(f"Port: {port}")
    print(f"Baud: {DEFAULT_SERIAL_BAUD}")
    print("=" * 50)

    ser = serial.Serial(
        port,
        DEFAULT_SERIAL_BAUD,
        timeout=1
    )

    time.sleep(2)

    print("ESP32 connected.")
    print("Waiting for telemetry...")
    print()

    while True:

        try:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            data["timestamp"] = time.time()

            save_record(data)

            print(
                f"T={data.get('temperature', 0):.2f} °C | "
                f"I={data.get('current', 0):.2f} A | "
                f"V={data.get('vibration_rms', 0):.3f} g"
            )

        except KeyboardInterrupt:

            print("\nBridge stopped.")
            break

        except Exception as e:

            print("Serial error:", e)
            time.sleep(1)

    ser.close()


if __name__ == "__main__":

    ports = find_serial_ports()

    print("Available serial ports:")

    for p in ports:
        print(" -", p)

    if not ports:
        print("No ESP32 detected.")
        print("Connect ESP32 using USB.")
    else:
        selected = input(
            f"\nEnter port [{ports[0]}]: "
        ).strip()

        if not selected:
            selected = ports[0]

        run(selected)