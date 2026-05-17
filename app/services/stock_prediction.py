from statistics import mean

from app.services.sales_forecast import (
    forecast_next_days,
    detect_sales_anomaly,
)


def predict_stock_risk(products: list):
    alerts = []

    for product in products:
        stock = product.get("stock", 0)

        sales_history = product.get(
            "daily_sales",
            []
        )

        if len(sales_history) < 3:
            continue

        forecasts = forecast_next_days(
            sales_history
        )

        if not forecasts:
            continue

        avg_future_sales = mean(forecasts)

        if avg_future_sales <= 0:
            continue

        days_remaining = (
            stock / avg_future_sales
        )

        if days_remaining <= 3:
            level = "critical"

        elif days_remaining <= 7:
            level = "high"

        elif days_remaining <= 15:
            level = "medium"

        else:
            level = None

        if level:
            alerts.append({
                "notification_type": "STOCK",

                "level": level,

                "title":
                    "Prévision de rupture de stock",

                "message": (
                    f"Le produit "
                    f"{product['name']} "
                    f"risque une rupture "
                    f"dans "
                    f"{round(days_remaining, 1)} "
                    f"jours."
                ),
            })

        anomaly = detect_sales_anomaly(
            sales_history
        )

        if anomaly:
            alerts.append({
                "notification_type": "AI",

                "level": anomaly["level"],

                "title":
                    "Anomalie ventes détectée",

                "message":
                    f"{product['name']} : "
                    f"{anomaly['message']}",
            })

    return alerts