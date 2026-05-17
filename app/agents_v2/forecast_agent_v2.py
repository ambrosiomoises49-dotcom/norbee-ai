from typing import Any, Dict

from app.agents_v2.base_agent import (
    build_agent_result,
    signal,
    risk,
    decision,
)


def run_forecast_agent_v2(
    forecast: Dict[str, Any],
    feature_store: Dict[str, Any],
) -> Dict[str, Any]:
    sales_forecast = forecast.get("sales", {})
    profit_forecast = forecast.get("profit", {})

    sales_trend = sales_forecast.get("trend", "stable")
    profit_trend = profit_forecast.get("trend", "stable")

    signals = [
        signal("sales_forecast_model", sales_forecast.get("model"), "info", "Modèle utilisé pour les ventes."),
        signal("profit_forecast_model", profit_forecast.get("model"), "info", "Modèle utilisé pour le profit."),
        signal("sales_forecast_trend", sales_trend, "warning" if sales_trend == "down" else "info", "Tendance prédite des ventes."),
        signal("profit_forecast_trend", profit_trend, "warning" if profit_trend == "down" else "info", "Tendance prédite du profit."),
    ]

    risks = []
    decisions = []

    if sales_trend == "down":
        risks.append(
            risk(
                "forecast_sales_decline",
                "medium",
                "Prévision de baisse des ventes",
                "Le modèle prévoit une tendance baissière des ventes.",
            )
        )
        decisions.append(
            decision(
                "forecast_commercial_action",
                "medium",
                "Prévenir la baisse des ventes",
                "Préparer promotions ciblées et renforcer les produits à forte rotation.",
                "Les prévisions indiquent une baisse possible.",
            )
        )

    if profit_trend == "down":
        risks.append(
            risk(
                "forecast_profit_decline",
                "high",
                "Prévision de baisse du profit",
                "Le modèle prévoit une tendance baissière du profit.",
            )
        )

    return build_agent_result(
        agent="forecast_agent_v2",
        summary=f"Prévision ventes: {sales_trend}. Prévision profit: {profit_trend}.",
        signals=signals,
        risks=risks,
        decisions=decisions,
    )