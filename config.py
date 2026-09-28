# System Configuration
# Update this to match your active ESP32 connection (e.g., "COM10")
SERIAL_PORT = "COM10"
BAUD_RATE = 115200

# EdgeGuard Local Hardware Protection Thresholds
LOCAL_PROTECTION_TEMP_MAX = 75.0     # Degrees C
LOCAL_PROTECTION_CURRENT_MAX = 2.5   # Amperes
LOCAL_PROTECTION_VIB_MAX = 0.75      # g (RMS)

DASHBOARD_REFRESH_RATE = 1.0 # Seconds