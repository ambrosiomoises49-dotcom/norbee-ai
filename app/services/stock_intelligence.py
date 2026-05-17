from app.schemas.analysis import ProductInput, AlertOutput


def analyze_stock_risk(products: list[ProductInput]) -> list[AlertOutput]:
    alerts: list[AlertOutput] = []

    for product in products:
        daily_velocity = product.sales_last_30_days / 30 if product.sales_last_30_days > 0 else 0

        if product.current_stock <= product.min_stock:
            alerts.append(
                AlertOutput(
                    level="critical",
                    title="Risque de rupture immédiate",
                    message=f"Le produit {product.name} est au niveau minimum ou en dessous du stock minimum.",
                    product_id=product.id,
                )
            )

        elif daily_velocity > 0:
            estimated_days_left = product.current_stock / daily_velocity

            if estimated_days_left <= 7:
                alerts.append(
                    AlertOutput(
                        level="high",
                        title="Rupture probable sous 7 jours",
                        message=f"Le produit {product.name} pourrait être en rupture dans environ {estimated_days_left:.1f} jours.",
                        product_id=product.id,
                    )
                )

    return alerts