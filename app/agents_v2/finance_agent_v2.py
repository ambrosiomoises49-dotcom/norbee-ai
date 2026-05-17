from typing import Any, Dict

from app.agents_v2.base_agent import (
    build_agent_result,
    signal,
    risk,
    decision,
)


def run_finance_agent_v2(
    feature_store: Dict[str, Any],
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    finance = feature_store.get("finance", {})
    sales = feature_store.get("sales", {})
    forecasting = feature_store.get("forecasting", {})

    cashflow = float(finance.get("cashflow_estimation") or 0)
    operating_ratio = float(finance.get("operating_ratio") or 0)
    margin = float(sales.get("profit_margin_rate") or 0)
    profit_growth = float(forecasting.get("profit_growth_rate") or 0)

    signals = [
        signal("cashflow_estimation", cashflow, "danger" if cashflow < 0 else "info", "Cashflow estimé."),
        signal("operating_ratio", operating_ratio, "danger" if operating_ratio > 75 else "info", "Poids des coûts sur les ventes."),
        signal("profit_margin_rate", margin, "warning" if margin < 15 else "info", "Marge estimée."),
        signal("profit_growth_rate", profit_growth, "warning" if profit_growth < 0 else "info", "Évolution du bénéfice."),
    ]

    risks = []
    decisions = []

    if cashflow < 0:
        risks.append(
            risk(
                "negative_cashflow",
                "high",
                "Cashflow négatif",
                f"Le cashflow estimé est de {cashflow:.2f}.",
            )
        )
        decisions.append(
            decision(
                "cash_control",
                "high",
                "Contrôler le cashflow",
                "Limiter les achats non urgents et accélérer les ventes rapides.",
                "Le cashflow estimé est négatif.",
            )
        )

    if operating_ratio > 75:
        risks.append(
            risk(
                "high_cost_pressure",
                "high",
                "Coûts trop élevés",
                f"Les coûts représentent {operating_ratio:.2f}% des ventes.",
            )
        )
        decisions.append(
            decision(
                "reduce_costs",
                "high",
                "Réduire les coûts",
                "Auditer les catégories de coûts dominantes et négocier fournisseurs.",
                "Les coûts pèsent trop lourd sur l’activité.",
            )
        )

    if margin < 15:
        decisions.append(
            decision(
                "margin_recovery",
                "medium",
                "Restaurer la marge",
                "Revoir prix, coûts d’achat et produits à faible rentabilité.",
                "La marge estimée est faible.",
            )
        )

    summary = (
        f"Cashflow estimé: {cashflow:.2f}. "
        f"Ratio coûts/ventes: {operating_ratio:.2f}%."
    )

    return build_agent_result(
        agent="finance_agent_v2",
        summary=summary,
        signals=signals,
        risks=risks,
        decisions=decisions,
    )