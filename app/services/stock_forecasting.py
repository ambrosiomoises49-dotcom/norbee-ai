from app.schemas.analysis import ProductInput, AlertOutput
from app.utils.i18n import t


def calculate_daily_velocity(product: ProductInput) -> float:
    if product.sales_last_30_days > 0:
        return product.sales_last_30_days / 30

    if product.sales_last_7_days > 0:
        return product.sales_last_7_days / 7

    return 0


def calculate_days_until_stockout(product: ProductInput) -> float | None:
    daily_velocity = calculate_daily_velocity(product)

    if daily_velocity <= 0:
        return None

    return product.current_stock / daily_velocity


def calculate_stock_risk_score(product: ProductInput) -> int:
    days_left = calculate_days_until_stockout(product)

    if product.current_stock <= 0:
        return 100

    if product.current_stock <= product.min_stock:
        return 90

    if days_left is None:
        return 10

    if days_left <= 3:
        return 85

    if days_left <= 7:
        return 70

    if days_left <= 14:
        return 45

    if days_left <= 30:
        return 25

    return 10


def calculate_reorder_quantity(product: ProductInput) -> float:
    daily_velocity = calculate_daily_velocity(product)
    security_days = 14
    target_stock = daily_velocity * security_days
    recommended = max(target_stock - product.current_stock, product.min_stock)

    return round(recommended, 2)


def calculate_estimated_lost_revenue(product: ProductInput) -> float:
    daily_velocity = calculate_daily_velocity(product)

    if daily_velocity <= 0:
        return 0

    estimated_days_lost = 7
    return round(daily_velocity * estimated_days_lost * product.sale_price, 2)


def forecast_stock_risk(
    products: list[ProductInput],
    lang: str = "pt",
) -> list[AlertOutput]:
    alerts: list[AlertOutput] = []

    for product in products:
        days_left = calculate_days_until_stockout(product)
        risk_score = calculate_stock_risk_score(product)
        reorder_quantity = calculate_reorder_quantity(product)
        lost_revenue = calculate_estimated_lost_revenue(product)

        if risk_score >= 90:
            alerts.append(
                AlertOutput(
                    level="critical",
                    title=t("critical_stockout_title", lang),
                    message=t(
                        "critical_stockout_message",
                        lang,
                        product=product.name,
                        stock=product.current_stock,
                        min_stock=product.min_stock,
                    ),
                    product_id=product.id,
                    risk_score=risk_score,
                    days_until_stockout=days_left,
                    recommended_reorder_quantity=reorder_quantity,
                    estimated_lost_revenue=lost_revenue,
                )
            )

        elif risk_score >= 70 and days_left is not None:
            alerts.append(
                AlertOutput(
                    level="high",
                    title=t("probable_stockout_title", lang),
                    message=t(
                        "probable_stockout_message",
                        lang,
                        product=product.name,
                        days=round(days_left, 1),
                    ),
                    product_id=product.id,
                    risk_score=risk_score,
                    days_until_stockout=days_left,
                    recommended_reorder_quantity=reorder_quantity,
                    estimated_lost_revenue=lost_revenue,
                )
            )

        elif risk_score >= 45 and days_left is not None:
            alerts.append(
                AlertOutput(
                    level="medium",
                    title=t("stock_to_watch_title", lang),
                    message=t(
                        "stock_to_watch_message",
                        lang,
                        product=product.name,
                        days=round(days_left, 1),
                    ),
                    product_id=product.id,
                    risk_score=risk_score,
                    days_until_stockout=days_left,
                    recommended_reorder_quantity=reorder_quantity,
                    estimated_lost_revenue=lost_revenue,
                )
            )

    return alerts