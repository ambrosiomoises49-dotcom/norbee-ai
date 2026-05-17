from typing import Any, Dict, List


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def calculate_margin_rate(revenue: float, gross_profit: float) -> float:
    if revenue <= 0:
        return 0.0

    return (gross_profit / revenue) * 100


def build_pricing_recommendations(
    rich_dataset: Dict[str, Any],
    feature_store: Dict[str, Any],
) -> Dict[str, Any]:
    sales_by_product = rich_dataset.get("sales_by_product", [])
    stock_risks = rich_dataset.get("stock_risks", [])

    stock_risk_product_ids = {
        item.get("id")
        for item in stock_risks
    }

    recommendations: List[Dict[str, Any]] = []

    for product in sales_by_product:
        product_id = product.get("id")
        product_name = product.get("name")

        quantity_sold = safe_float(product.get("quantity_sold"))
        revenue = safe_float(product.get("revenue"))
        gross_profit = safe_float(product.get("gross_profit"))

        margin_rate = calculate_margin_rate(
            revenue=revenue,
            gross_profit=gross_profit,
        )

        has_stock_risk = product_id in stock_risk_product_ids

        decision = "keep_price"
        priority = "low"
        suggested_change_percent = 0.0
        reason = "Le prix semble stable pour le moment."

        if revenue > 0 and gross_profit < 0:
            decision = "increase_price"
            priority = "high"
            suggested_change_percent = 15.0
            reason = (
                "Le produit génère une marge négative. "
                "Il faut augmenter le prix ou réduire le coût d’achat."
            )

        elif has_stock_risk and quantity_sold > 0:
            decision = "increase_price"
            priority = "medium"
            suggested_change_percent = 5.0
            reason = (
                "Le produit se vend et présente un risque de rupture. "
                "Une légère hausse peut protéger la marge et ralentir la rupture."
            )

        elif margin_rate < 10 and revenue > 0:
            decision = "increase_price"
            priority = "medium"
            suggested_change_percent = 8.0
            reason = (
                "La marge est faible. Une hausse modérée peut améliorer la rentabilité."
            )

        elif margin_rate > 35 and quantity_sold <= 2:
            decision = "promotion"
            priority = "medium"
            suggested_change_percent = -5.0
            reason = (
                "La marge est élevée mais les ventes sont faibles. "
                "Une petite promotion peut tester la demande."
            )

        elif quantity_sold == 0 and revenue == 0:
            decision = "promotion"
            priority = "low"
            suggested_change_percent = -10.0
            reason = (
                "Le produit ne se vend pas sur la période. "
                "Tester une réduction ou améliorer l’exposition."
            )

        recommendations.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "decision": decision,
                "priority": priority,
                "quantity_sold": round(quantity_sold, 2),
                "revenue": round(revenue, 2),
                "gross_profit": round(gross_profit, 2),
                "margin_rate": round(margin_rate, 2),
                "has_stock_risk": has_stock_risk,
                "suggested_change_percent": suggested_change_percent,
                "reason": reason,
            }
        )

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    recommendations = sorted(
        recommendations,
        key=lambda item: priority_order.get(item["priority"], 3),
    )

    return {
        "engine": "pricing_engine_v1",
        "recommendations": recommendations,
    }