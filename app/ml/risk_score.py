from typing import Dict, List


def calculate_ml_risk_score(
    sales_trend: str,
    profit_trend: str,
    sales_anomalies: List[Dict],
    profit_anomalies: List[Dict],
    stock_anomalies: List[Dict],
) -> Dict:
    score = 0

    if sales_trend == "down":
        score += 25

    if profit_trend == "down":
        score += 35

    if sales_anomalies:
        score += 15

    if profit_anomalies:
        score += 15

    if stock_anomalies:
        score += 10

    score = min(score, 100)

    if score >= 70:
        level = "high"
        label = "Risco elevado"
    elif score >= 40:
        level = "medium"
        label = "Risco moderado"
    else:
        level = "low"
        label = "Risco baixo"

    return {
        "score": score,
        "level": level,
        "label": label,
    }