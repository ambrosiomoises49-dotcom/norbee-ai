from typing import Any, Dict, List


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_transfer_recommendations(
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    sales_by_cantina = rich_dataset.get("sales_by_cantina", [])
    stock_risks = rich_dataset.get("stock_risks", [])

    recommendations: List[Dict[str, Any]] = []

    best_cantina = None

    if sales_by_cantina:
        best_cantina = max(
            sales_by_cantina,
            key=lambda item: safe_float(item.get("total_sales")),
        )

    for product in stock_risks:
        quantity = safe_float(product.get("quantity"))
        min_stock = safe_float(product.get("minStock"))

        if quantity <= min_stock and best_cantina:
            recommendations.append(
                {
                    "type": "transfer_or_purchase",
                    "priority": "high" if quantity <= 0 else "medium",
                    "product_id": product.get("id"),
                    "product_name": product.get("name"),
                    "current_stock": quantity,
                    "min_stock": min_stock,
                    "target_cantina_id": best_cantina.get("id"),
                    "target_cantina_name": best_cantina.get("name"),
                    "recommended_quantity": max(min_stock * 2 - quantity, min_stock, 1),
                    "reason": (
                        f"{product.get('name')} est sous le stock minimum. "
                        f"La cantina {best_cantina.get('name')} est la plus performante "
                        "et doit être priorisée si la demande continue."
                    ),
                    "action": (
                        f"Transférer ou acheter du stock pour {product.get('name')} "
                        f"vers {best_cantina.get('name')}."
                    ),
                }
            )

    return {
        "engine": "transfer_optimization_engine",
        "recommendations": recommendations,
    }