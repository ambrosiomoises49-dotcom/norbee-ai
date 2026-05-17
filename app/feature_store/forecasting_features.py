from typing import Any, Dict, List


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def calculate_growth_rate(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0

    first = safe_float(values[0])
    last = safe_float(values[-1])

    if first == 0:
        return 0.0

    return ((last - first) / abs(first)) * 100


def calculate_volatility(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0

    avg = sum(values) / len(values)

    if avg == 0:
        return 0.0

    variance = sum((v - avg) ** 2 for v in values) / len(values)

    return (variance ** 0.5) / abs(avg) * 100


def build_forecasting_features(
    ml_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    sales_history = [
        safe_float(v) for v in ml_dataset.get("sales_history", [])
    ]

    profit_history = [
        safe_float(v) for v in ml_dataset.get("profit_history", [])
    ]

    stock_history = [
        safe_float(v) for v in ml_dataset.get("stock_history", [])
    ]

    return {
        "sales_points": len(sales_history),
        "profit_points": len(profit_history),
        "stock_points": len(stock_history),

        "sales_growth_rate": round(calculate_growth_rate(sales_history), 2),
        "profit_growth_rate": round(calculate_growth_rate(profit_history), 2),

        "sales_volatility": round(calculate_volatility(sales_history), 2),
        "profit_volatility": round(calculate_volatility(profit_history), 2),

        "sales_last_value": sales_history[-1] if sales_history else 0,
        "profit_last_value": profit_history[-1] if profit_history else 0,
        "stock_last_value": stock_history[-1] if stock_history else 0,
    }