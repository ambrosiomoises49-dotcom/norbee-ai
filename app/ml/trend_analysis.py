from typing import Dict, List


def analyze_trend(history: List[float]) -> Dict:
    if len(history) < 2:
        return {
            "trend": "stable",
            "growth_rate": 0,
            "message": "Dados insuficientes.",
        }

    first = history[0]
    last = history[-1]

    if first == 0:
        growth_rate = 0
    else:
        growth_rate = ((last - first) / abs(first)) * 100

    if growth_rate > 10:
        trend = "strong_growth"
        message = "Croissance forte détectée."
    elif growth_rate > 0:
        trend = "growth"
        message = "Croissance modérée détectée."
    elif growth_rate < -10:
        trend = "strong_decline"
        message = "Forte baisse détectée."
    elif growth_rate < 0:
        trend = "decline"
        message = "Baisse modérée détectée."
    else:
        trend = "stable"
        message = "Activité stable."

    return {
        "trend": trend,
        "growth_rate": round(growth_rate, 2),
        "message": message,
    }