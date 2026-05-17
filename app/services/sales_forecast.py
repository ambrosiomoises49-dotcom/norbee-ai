from statistics import mean


def calculate_trend(values: list[float]):
    if len(values) < 2:
        return 0

    first = values[: len(values) // 2]
    second = values[len(values) // 2 :]

    return mean(second) - mean(first)


def forecast_next_days(
    sales_history: list[float],
    days: int = 7,
):
    if len(sales_history) < 3:
        return []

    avg = mean(sales_history)

    trend = calculate_trend(sales_history)

    forecasts = []

    current = avg

    for _ in range(days):
        current += trend * 0.15

        if current < 0:
            current = 0

        forecasts.append(round(current, 2))

    return forecasts


def detect_sales_anomaly(
    sales_history: list[float],
):
    if len(sales_history) < 5:
        return None

    avg_sales = mean(sales_history)

    last_value = sales_history[-1]

    if last_value < avg_sales * 0.4:
        return {
            "level": "high",
            "message": (
                "Baisse anormale des ventes détectée."
            ),
        }

    if last_value > avg_sales * 2:
        return {
            "level": "medium",
            "message": (
                "Hausse inhabituelle des ventes détectée."
            ),
        }

    return None