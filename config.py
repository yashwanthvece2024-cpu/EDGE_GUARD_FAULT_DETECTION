# System Configuration

# Serial Port Configuration (Update this based on your OS)
# Windows: "COM3", "COM4", etc.
# Linux/Raspberry Pi: "/dev/ttyUSB0" or "/dev/ttyACM0"
SERIAL_PORT = "COM3"
BAUD_RATE = 115200

# EdgeGuard Local Hardware Protection Thresholds
# These must match the logic programmed into the ESP32
LOCAL_PROTECTION_TEMP_MAX = 75.0     # Degrees C
LOCAL_PROTECTION_CURRENT_MAX = 2.5   # Amperes
LOCAL_PROTECTION_VIB_MAX = 0.75      # g (RMS)

# Dashboard Configuration
DASHBOARD_REFRESH_RATE = 1.0 # Seconds