from typing import Any, Dict

from app.agents_v2.base_agent import (
    build_agent_result,
    signal,
    risk,
    decision,
)


def run_sales_agent_v2(
    feature_store: Dict[str, Any],
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    sales = feature_store.get("sales", {})
    forecasting = feature_store.get("forecasting", {})

    total_sales = float(sales.get("total_sales") or 0)
    total_quantity = float(sales.get("total_quantity") or 0)
    sales_growth = float(forecasting.get("sales_growth_rate") or 0)
    sales_volatility = float(forecasting.get("sales_volatility") or 0)

    signals = [
        signal("total_sales", total_sales, "info", "Chiffre d’affaires total sur la période."),
        signal("total_quantity", total_quantity, "info", "Quantité totale vendue."),
        signal("sales_growth_rate", sales_growth, "warning" if sales_growth < 0 else "info", "Évolution des ventes."),
        signal("sales_volatility", sales_volatility, "warning" if sales_volatility > 80 else "info", "Instabilité des ventes."),
    ]

    risks = []
    decisions = []

    if sales_growth < -20:
        risks.append(
            risk(
                "sales_decline",
                "high",
                "Forte baisse des ventes",
                f"Les ventes diminuent de {sales_growth:.2f}%.",
            )
        )
        decisions.append(
            decision(
                "commercial_action",
                "high",
                "Lancer une action commerciale",
                "Identifier les produits en baisse et lancer une promotion ciblée.",
                "Les ventes sont en forte diminution.",
            )
        )

    if sales_volatility > 80:
        risks.append(
            risk(
                "sales_instability",
                "medium",
                "Ventes instables",
                f"La volatilité des ventes est de {sales_volatility:.2f}%.",
            )
        )

    top_product = sales.get("top_product")

    if top_product:
        decisions.append(
            decision(
                "boost_best_product",
                "medium",
                f"Renforcer le produit {top_product.get('name')}",
                "Garantir disponibilité, bonne exposition et marge correcte.",
                "Ce produit est le plus performant en chiffre d’affaires.",
            )
        )

    summary = (
        f"Ventes totales: {total_sales:.2f}. "
        f"Croissance ventes: {sales_growth:.2f}%."
    )

    return build_agent_result(
        agent="sales_agent_v2",
        summary=summary,
        signals=signals,
        risks=risks,
        decisions=decisions,
    )