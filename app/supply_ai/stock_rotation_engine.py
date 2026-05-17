from typing import Any, Dict, List


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def analyze_stock_rotation(
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    sales_by_product = rich_dataset.get("sales_by_product", [])
    stock_risks = rich_dataset.get("stock_risks", [])

    stock_map = {}

    for stock in stock_risks:
        stock_map[stock.get("productId")] = stock

    products_analysis = []

    for product in sales_by_product:
        product_id = product.get("productId")

        quantity_sold = safe_float(product.get("quantity"))
        revenue = safe_float(product.get("revenue"))

        stock_data = stock_map.get(product_id, {})

        current_stock = safe_float(stock_data.get("quantity"))
        min_stock = safe_float(stock_data.get("minStock"))

        daily_velocity = quantity_sold / 30 if quantity_sold > 0 else 0

        days_remaining = 999

        if daily_velocity > 0:
            days_remaining = current_stock / daily_velocity

        rotation_level = "slow"

        if daily_velocity >= 10:
            rotation_level = "very_fast"
        elif daily_velocity >= 5:
            rotation_level = "fast"
        elif daily_velocity >= 2:
            rotation_level = "medium"

        risk_level = "low"

        if days_remaining <= 3:
            risk_level = "critical"
        elif days_remaining <= 7:
            risk_level = "high"
        elif days_remaining <= 14:
            risk_level = "medium"

        products_analysis.append({
            "product_id": product_id,
            "product_name": product.get("name"),
            "quantity_sold": round(quantity_sold, 2),
            "revenue": round(revenue, 2),
            "current_stock": round(current_stock, 2),
            "min_stock": round(min_stock, 2),
            "daily_velocity": round(daily_velocity, 2),
            "estimated_days_remaining": round(days_remaining, 1),
            "rotation_level": rotation_level,
            "risk_level": risk_level,
        })

    critical_products = [
        p for p in products_analysis
        if p["risk_level"] in ["critical", "high"]
    ]

    fast_products = [
        p for p in products_analysis
        if p["rotation_level"] in ["fast", "very_fast"]
    ]

    return {
        "engine": "stock_rotation_engine",
        "products_analysis": products_analysis,
        "critical_products": critical_products,
        "fast_rotation_products": fast_products,
    }