import numpy as np
import pandas as pd

from config import FEATURES


def prepare_record(record):
    """
    Convert incoming telemetry into a clean numeric record.
    """

    temperature = float(record.get("temperature", 0.0))
    current = float(record.get("current", 0.0))
    vibration = float(record.get("vibration_rms", 0.0))

    temperature = max(0.0, temperature)
    current = max(0.0, current)
    vibration = max(0.0, vibration)

    return {
        "temperature": temperature,
        "current": current,
        "vibration_rms": vibration
    }


def record_to_dataframe(record):
    clean = prepare_record(record)

    return pd.DataFrame(
        [[
            clean["temperature"],
            clean["current"],
            clean["vibration_rms"]
        ]],
        columns=FEATURES
    )


def calculate_rule_status(record):

    temperature = float(record["temperature"])
    current = float(record["current"])
    vibration = float(record["vibration_rms"])

    if (
        temperature >= 75
        or current >= 2.5
        or vibration >= 0.75
    ):
        return "FAULT"

    if (
        temperature >= 55
        or current >= 1.5
        or vibration >= 0.35
    ):
        return "WARNING"

    return "NORMAL"


def calculate_health_index(record):

    temperature = float(record["temperature"])
    current = float(record["current"])
    vibration = float(record["vibration_rms"])

    temp_score = max(0, 100 - max(0, temperature - 35) * 1.5)
    current_score = max(0, 100 - max(0, current - 0.7) * 25)
    vibration_score = max(0, 100 - max(0, vibration - 0.10) * 70)

    score = (
        temp_score * 0.35
        + current_score * 0.30
        + vibration_score * 0.35
    )

    return round(float(np.clip(score, 0, 100)), 1)