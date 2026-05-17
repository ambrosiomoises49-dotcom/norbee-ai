from collections import defaultdict
from typing import Any, Dict, List

from app.schemas.sales import SaleInput


def analyze_sales_agent(sales: list[SaleInput], lang: str = "pt") -> Dict[str, Any]:
    total_revenue = sum(float(sale.total_amount or 0) for sale in sales)
    total_quantity = sum(float(sale.quantity or 0) for sale in sales)

    by_product = defaultdict(
        lambda: {
            "product_id": "",
            "product_name": "",
            "category": None,
            "quantity": 0.0,
            "revenue": 0.0,
            "gross_profit": 0.0,
        }
    )

    by_cantina = defaultdict(
        lambda: {
            "cantina_id": "",
            "cantina_name": "",
            "quantity": 0.0,
            "revenue": 0.0,
            "gross_profit": 0.0,
        }
    )

    for sale in sales:
        quantity = float(sale.quantity or 0)
        total_amount = float(sale.total_amount or 0)
        unit_price = float(sale.unit_price or 0)
        unit_cost = float(sale.unit_cost or 0)

        gross_profit = (unit_price - unit_cost) * quantity

        product_row = by_product[sale.product_id]
        product_row["product_id"] = sale.product_id
        product_row["product_name"] = sale.product_name
        product_row["category"] = sale.category
        product_row["quantity"] += quantity
        product_row["revenue"] += total_amount
        product_row["gross_profit"] += gross_profit

        cantina_key = sale.cantina_id or "GENERAL"
        cantina_row = by_cantina[cantina_key]
        cantina_row["cantina_id"] = sale.cantina_id or "GENERAL"
        cantina_row["cantina_name"] = sale.cantina_name or "Geral"
        cantina_row["quantity"] += quantity
        cantina_row["revenue"] += total_amount
        cantina_row["gross_profit"] += gross_profit

    top_products = sorted(
        by_product.values(),
        key=lambda item: float(item["revenue"] or 0),
        reverse=True,
    )[:10]

    top_cantinas = sorted(
        by_cantina.values(),
        key=lambda item: float(item["revenue"] or 0),
        reverse=True,
    )[:10]

    recommendations: List[str] = []

    if top_products:
        recommendations.append(
            "Renforcer le stock des produits les plus vendus."
        )

    if top_cantinas:
        recommendations.append(
            "Analyser les cantines avec forte performance pour reproduire leur stratégie."
        )

    if total_revenue <= 0:
        recommendations.append(
            "Aucune vente significative détectée. Vérifier l’activité commerciale."
        )

    return {
        "agent": "sales_agent",
        "status": "ok",
        "total_sales_records": len(sales),
        "total_revenue": round(total_revenue, 2),
        "total_quantity": round(total_quantity, 2),
        "top_products": top_products,
        "top_cantinas": top_cantinas,
        "recommendations": recommendations,
    }


def analyze_sales(sales: list[SaleInput], lang: str = "pt") -> Dict[str, Any]:
    """
    Alias stable utilisé par app/routes/alerts.py.
    Garde la compatibilité avec l'ancien nom analyze_sales_agent.
    """
    return analyze_sales_agent(sales=sales, lang=lang)