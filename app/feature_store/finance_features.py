from typing import Dict, Any


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_finance_features(dataset: Dict[str, Any]) -> Dict[str, Any]:
    costs_by_category = dataset.get("costs_by_category", [])
    sales_by_product = dataset.get("sales_by_product", [])

    total_costs = 0
    total_revenue = 0
    total_profit = 0

    for cost in costs_by_category:
        total_costs += safe_float(cost.get("total_cost"))

    for product in sales_by_product:
        total_revenue += safe_float(product.get("revenue"))
        total_profit += safe_float(product.get("gross_profit"))

    cashflow_estimation = total_revenue - total_costs

    operating_ratio = 0

    if total_revenue > 0:
        operating_ratio = (total_costs / total_revenue) * 100

    financial_health = "healthy"

    if operating_ratio > 90:
        financial_health = "critical"

    elif operating_ratio > 70:
        financial_health = "warning"

    return {
        "total_costs": round(total_costs, 2),
        "cashflow_estimation": round(cashflow_estimation, 2),
        "operating_ratio": round(operating_ratio, 2),
        "financial_health": financial_health,
    }