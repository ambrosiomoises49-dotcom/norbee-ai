from typing import List, Dict
import numpy as np


def simple_sales_forecast(history: List[float], periods: int = 7) -> Dict:
    """
    Prévision simple basée sur tendance moyenne.
    """

    if not history:
        return {
            "forecast": [],
            "trend": "stable",
            "average": 0,
        }

    values = np.array(history, dtype=float)

    avg = float(np.mean(values))

    if len(values) >= 2:
        trend_value = values[-1] - values[0]
    else:
        trend_value = 0

    if trend_value > 0:
        trend = "up"
    elif trend_value < 0:
        trend = "down"
    else:
        trend = "stable"

    growth_factor = 1 + (trend_value / max(abs(values[0]), 1)) * 0.1

    future = []

    current = values[-1]

    for _ in range(periods):
        current = current * growth_factor
        future.append(round(float(current), 2))

    return {
        "forecast": future,
        "trend": trend,
        "average": round(avg, 2),
    }