from typing import Dict, List

import numpy as np
from sklearn.linear_model import LinearRegression


def advanced_sales_forecast(
    history: List[float],
    periods: int = 7,
) -> Dict:

    if len(history) < 5:
        return {
            "status": "fallback",
            "reason": "not_enough_data",
            "forecast": [],
            "trend": "stable",
        }

    values = np.array(history, dtype=float)

    X = np.arange(len(values)).reshape(-1, 1)
    y = values

    model = LinearRegression()
    model.fit(X, y)

    future_x = np.arange(
        len(values),
        len(values) + periods,
    ).reshape(-1, 1)

    predictions = model.predict(future_x)

    predictions = [
        max(round(float(p), 2), 0)
        for p in predictions
    ]

    slope = model.coef_[0]

    if slope > 0:
        trend = "up"
    elif slope < 0:
        trend = "down"
    else:
        trend = "stable"

    return {
        "status": "ok",
        "model": "LinearRegression",
        "trend": trend,
        "slope": round(float(slope), 4),
        "forecast": predictions,
    }