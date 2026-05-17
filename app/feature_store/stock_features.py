from typing import Dict, Any


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_stock_features(dataset: Dict[str, Any]) -> Dict[str, Any]:
    stock_risks = dataset.get("stock_risks", [])

    critical_products = []
    stock_health_score = 100

    for product in stock_risks:
        quantity = safe_float(product.get("quantity"))
        min_stock = safe_float(product.get("minStock"))

        risk_ratio = 0

        if min_stock > 0:
            risk_ratio = quantity / min_stock

        days_remaining = quantity / 3 if quantity > 0 else 0

        critical_products.append({
            "product": product.get("name"),
            "quantity": quantity,
            "min_stock": min_stock,
            "risk_ratio": round(risk_ratio, 2),
            "estimated_days_remaining": round(days_remaining, 1),
        })

        if quantity <= 0:
            stock_health_score -= 20

        elif quantity < min_stock:
            stock_health_score -= 10

    stock_health_score = max(stock_health_score, 0)

    return {
        "stock_health_score": stock_health_score,
        "critical_products": critical_products,
        "critical_products_count": len(critical_products),
    }