from typing import List, Dict
import numpy as np


def detect_anomalies(values: List[float]) -> Dict:
    if len(values) < 3:
        return {
            "anomalies": [],
            "status": "not_enough_data",
        }

    arr = np.array(values, dtype=float)

    mean = np.mean(arr)
    std = np.std(arr)

    anomalies = []

    for i, value in enumerate(arr):
        z_score = (value - mean) / std if std > 0 else 0

        if abs(z_score) > 2:
            anomalies.append(
                {
                    "index": i,
                    "value": float(value),
                    "z_score": round(float(z_score), 2),
                }
            )

    return {
        "status": "ok",
        "anomalies": anomalies,
        "mean": round(float(mean), 2),
        "std": round(float(std), 2),
    }