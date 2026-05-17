from app.ml.sales_forecast import simple_sales_forecast
from app.ml.advanced_forecast import advanced_sales_forecast


def smart_forecast(history, periods=7):
    if len(history) >= 5:
        result = advanced_sales_forecast(
            history=history,
            periods=periods,
        )

        if result["status"] == "ok":
            return result

    return simple_sales_forecast(
        history=history,
        periods=periods,
    )