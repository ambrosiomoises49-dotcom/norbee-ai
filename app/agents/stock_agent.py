from typing import Any, Dict, List

from app.schemas.analysis import ProductInput, AlertOutput


def analyze_stock(products: List[ProductInput]) -> List[AlertOutput]:
    alerts: List[AlertOutput] = []

    for product in products:
        current_stock = float(product.current_stock or 0)
        min_stock = float(product.min_stock or 0)
        sales_30 = float(product.sales_last_30_days or 0)

        daily_sales_avg = sales_30 / 30 if sales_30 > 0 else 0

        days_until_stockout = (
            current_stock / daily_sales_avg if daily_sales_avg > 0 else 999
        )

        if current_stock <= min_stock:
            recommended_reorder_quantity = max(min_stock * 2 - current_stock, 0)

            alerts.append(
                AlertOutput(
                    level="high",
                    title=f"Stock baixo: {product.name}",
                    message=f"O produto {product.name} está abaixo do stock mínimo.",
                    product_id=product.id,
                    risk_score=90,
                    days_until_stockout=round(days_until_stockout, 1),
                    recommended_reorder_quantity=round(
                        recommended_reorder_quantity, 1
                    ),
                    estimated_lost_revenue=round(
                        recommended_reorder_quantity * float(product.sale_price or 0),
                        2,
                    ),
                )
            )

        elif days_until_stockout <= 7:
            alerts.append(
                AlertOutput(
                    level="medium",
                    title=f"Risco de ruptura: {product.name}",
                    message=f"O produto {product.name} pode acabar em breve.",
                    product_id=product.id,
                    risk_score=70,
                    days_until_stockout=round(days_until_stockout, 1),
                    recommended_reorder_quantity=round(max(min_stock * 2, 1), 1),
                    estimated_lost_revenue=round(
                        current_stock * float(product.sale_price or 0),
                        2,
                    ),
                )
            )

    return alerts


def analyze_stock_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compatibilité avec l’ancienne route app/routes/stock_agent.py.
    Accepte un dictionnaire et retourne une analyse simple.
    """
    raw_products = data.get("products", []) if isinstance(data, dict) else []

    products: List[ProductInput] = []

    for item in raw_products:
        try:
            products.append(ProductInput(**item))
        except Exception:
            continue

    alerts = analyze_stock(products)

    return {
        "agent": "stock_agent",
        "status": "ok",
        "alerts": [alert.model_dump() for alert in alerts],
        "alerts_count": len(alerts),
        "summary": (
            "Riscos de stock encontrados."
            if alerts
            else "Nenhum risco crítico de stock encontrado."
        ),
    }