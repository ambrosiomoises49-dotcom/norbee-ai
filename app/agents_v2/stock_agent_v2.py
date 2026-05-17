from typing import Any, Dict

from app.agents_v2.base_agent import (
    build_agent_result,
    signal,
    risk,
    decision,
)


def run_stock_agent_v2(
    feature_store: Dict[str, Any],
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    stock = feature_store.get("stock", {})

    stock_health = float(stock.get("stock_health_score") or 0)
    critical_products = stock.get("critical_products", [])

    signals = [
        signal("stock_health_score", stock_health, "danger" if stock_health < 70 else "info", "Score global de santé du stock."),
        signal("critical_products_count", len(critical_products), "danger" if critical_products else "info", "Nombre de produits critiques."),
    ]

    risks = []
    decisions = []

    if stock_health < 70:
        risks.append(
            risk(
                "stock_health_low",
                "high",
                "Santé du stock faible",
                f"Le score stock est de {stock_health:.0f}/100.",
            )
        )

    for product in critical_products[:5]:
        risks.append(
            risk(
                "critical_product",
                "high",
                f"Produit critique: {product.get('product')}",
                f"Stock actuel: {product.get('quantity')}, minimum: {product.get('min_stock')}.",
            )
        )
        decisions.append(
            decision(
                "purchase",
                "high",
                f"Réapprovisionner {product.get('product')}",
                "Acheter ou transférer du stock immédiatement.",
                "Le produit est sous le stock minimum ou en rupture.",
            )
        )

    summary = (
        f"Score stock: {stock_health:.0f}/100. "
        f"Produits critiques: {len(critical_products)}."
    )

    return build_agent_result(
        agent="stock_agent_v2",
        summary=summary,
        signals=signals,
        risks=risks,
        decisions=decisions,
    )