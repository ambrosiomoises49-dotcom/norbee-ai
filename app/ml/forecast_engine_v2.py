from typing import Any, Dict, List

import numpy as np

from app.ml.smart_forecast import smart_forecast


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def forecast_with_xgboost(history: List[float], periods: int = 30) -> Dict[str, Any]:
    try:
        from xgboost import XGBRegressor
    except Exception:
        return {
            "status": "unavailable",
            "model": "xgboost",
            "reason": "xgboost_not_installed",
            "forecast": [],
        }

    values = np.array([safe_float(v) for v in history], dtype=float)

    if len(values) < 10:
        return {
            "status": "fallback",
            "model": "xgboost",
            "reason": "not_enough_data",
            "forecast": [],
        }

    X = np.arange(len(values)).reshape(-1, 1)
    y = values

    model = XGBRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        objective="reg:squarederror",
        random_state=42,
    )

    model.fit(X, y)

    future_x = np.arange(
        len(values),
        len(values) + periods,
    ).reshape(-1, 1)

    predictions = model.predict(future_x)

    forecast = [
        max(round(float(value), 2), 0)
        for value in predictions
    ]

    trend = "stable"

    if forecast and len(values) > 0:
        if forecast[-1] > values[-1]:
            trend = "up"
        elif forecast[-1] < values[-1]:
            trend = "down"

    return {
        "status": "ok",
        "model": "xgboost",
        "trend": trend,
        "forecast": forecast,
    }


def forecast_with_prophet(history: List[float], periods: int = 30) -> Dict[str, Any]:
    try:
        import pandas as pd
        from prophet import Prophet
    except Exception:
        return {
            "status": "unavailable",
            "model": "prophet",
            "reason": "prophet_not_installed",
            "forecast": [],
        }

    values = [safe_float(v) for v in history]

    if len(values) < 14:
        return {
            "status": "fallback",
            "model": "prophet",
            "reason": "not_enough_data",
            "forecast": [],
        }

    df = pd.DataFrame(
        {
            "ds": pd.date_range(
                end=pd.Timestamp.today(),
                periods=len(values),
                freq="D",
            ),
            "y": values,
        }
    )

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False,
    )

    model.fit(df)

    future = model.make_future_dataframe(
        periods=periods,
        freq="D",
    )

    forecast_df = model.predict(future)

    predictions = forecast_df.tail(periods)["yhat"].tolist()

    forecast = [
        max(round(float(value), 2), 0)
        for value in predictions
    ]

    trend = "stable"

    if forecast and values:
        if forecast[-1] > values[-1]:
            trend = "up"
        elif forecast[-1] < values[-1]:
            trend = "down"

    return {
        "status": "ok",
        "model": "prophet",
        "trend": trend,
        "forecast": forecast,
    }


def hybrid_forecast(history: List[float], periods: int = 30) -> Dict[str, Any]:
    values = [safe_float(v) for v in history]

    if len(values) >= 30:
        prophet_result = forecast_with_prophet(values, periods)

        if prophet_result["status"] == "ok":
            return prophet_result

    if len(values) >= 10:
        xgb_result = forecast_with_xgboost(values, periods)

        if xgb_result["status"] == "ok":
            return xgb_result

    fallback = smart_forecast(
        history=values,
        periods=periods,
    )

    fallback["model"] = fallback.get("model", "smart_fallback")
    fallback["status"] = fallback.get("status", "fallback")

    return fallback


def predict_stockout_probability(
    current_stock: float,
    min_stock: float,
    sales_history: List[float],
    periods: int = 30,
) -> Dict[str, Any]:
    current_stock = safe_float(current_stock)
    min_stock = safe_float(min_stock)

    forecast = hybrid_forecast(
        history=sales_history,
        periods=periods,
    )

    demand_forecast = forecast.get("forecast", [])

    cumulative_demand = 0
    stockout_day = None

    for index, demand in enumerate(demand_forecast, start=1):
        cumulative_demand += safe_float(demand)

        if current_stock - cumulative_demand <= 0:
            stockout_day = index
            break

    probability = 0

    if stockout_day is not None:
        probability = max(10, 100 - (stockout_day * 3))
    elif current_stock <= min_stock:
        probability = 70
    elif min_stock > 0 and current_stock < min_stock * 1.5:
        probability = 45

    return {
        "model": "stockout_probability_v1",
        "stockout_probability": min(round(probability, 2), 100),
        "stockout_day": stockout_day,
        "forecasted_demand": demand_forecast,
        "forecast_model": forecast.get("model"),
    }