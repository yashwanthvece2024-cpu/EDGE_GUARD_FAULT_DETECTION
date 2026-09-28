from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

TELEMETRY_FILE = DATA_DIR / "telemetry.jsonl"
MODEL_FILE = MODEL_DIR / "edgeguard_svm.pkl"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "temperature",
    "current",
    "vibration_rms"
]

DEFAULT_SERIAL_BAUD = 115200

NORMAL_TEMP_MAX = 55.0
WARNING_TEMP_MAX = 75.0

NORMAL_CURRENT_MAX = 1.5
WARNING_CURRENT_MAX = 2.5

NORMAL_VIBRATION_MAX = 0.35
WARNING_VIBRATION_MAX = 0.75