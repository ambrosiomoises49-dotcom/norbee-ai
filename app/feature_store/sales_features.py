from typing import Dict, Any, List


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_sales_features(dataset: Dict[str, Any]) -> Dict[str, Any]:
    sales_by_product = dataset.get("sales_by_product", [])
    sales_by_cantina = dataset.get("sales_by_cantina", [])

    total_sales = 0
    total_profit = 0
    total_quantity = 0

    top_product = None
    weak_product = None

    for product in sales_by_product:
        revenue = safe_float(product.get("revenue"))
        profit = safe_float(product.get("gross_profit"))
        quantity = safe_float(product.get("quantity"))

        total_sales += revenue
        total_profit += profit
        total_quantity += quantity

    if sales_by_product:
        top_product = max(
            sales_by_product,
            key=lambda x: safe_float(x.get("revenue")),
        )

        weak_product = min(
            sales_by_product,
            key=lambda x: safe_float(x.get("revenue")),
        )

    average_ticket = 0

    if total_quantity > 0:
        average_ticket = total_sales / total_quantity

    sales_velocity = 0

    if len(sales_by_product) > 0:
        sales_velocity = total_quantity / len(sales_by_product)

    profit_margin_rate = 0

    if total_sales > 0:
        profit_margin_rate = (total_profit / total_sales) * 100

    cantina_sales_distribution = []

    for cantina in sales_by_cantina:
        cantina_sales_distribution.append({
            "cantina": cantina.get("name"),
            "sales": safe_float(cantina.get("total_sales")),
        })

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_quantity": round(total_quantity, 2),

        "average_ticket": round(average_ticket, 2),
        "sales_velocity": round(sales_velocity, 2),
        "profit_margin_rate": round(profit_margin_rate, 2),

        "top_product": top_product,
        "weak_product": weak_product,

        "cantina_sales_distribution": cantina_sales_distribution,
    }