from typing import Any, Dict, List


def build_purchase_recommendations(
    stock_rotation: Dict[str, Any],
) -> Dict[str, Any]:
    recommendations = []

    critical_products = stock_rotation.get(
        "critical_products",
        [],
    )

    for product in critical_products:
        velocity = float(product.get("daily_velocity") or 0)

        target_days = 21

        recommended_quantity = velocity * target_days

        urgency = "low"

        if product["risk_level"] == "critical":
            urgency = "high"
        elif product["risk_level"] == "high":
            urgency = "medium"

        recommendations.append({
            "type": "purchase",
            "urgency": urgency,
            "product_id": product.get("product_id"),
            "product_name": product.get("product_name"),
            "current_stock": product.get("current_stock"),
            "daily_velocity": velocity,
            "estimated_days_remaining": product.get(
                "estimated_days_remaining"
            ),
            "recommended_purchase_quantity": round(
                recommended_quantity,
                2,
            ),
            "reason": (
                f"Produit à rotation {product.get('rotation_level')} "
                f"avec risque {product.get('risk_level')}."
            ),
        })

    recommendations = sorted(
        recommendations,
        key=lambda x: (
            0 if x["urgency"] == "high" else 1
        ),
    )

    return {
        "engine": "purchase_recommendation_engine",
        "recommendations": recommendations,
    }