from typing import Any, Dict


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_cantina_features(dataset: Dict[str, Any]) -> Dict[str, Any]:
    cantinas = dataset.get("sales_by_cantina", [])

    total_sales = sum(safe_float(c.get("total_sales")) for c in cantinas)
    active_cantinas = [
        c for c in cantinas if safe_float(c.get("total_sales")) > 0
    ]

    inactive_cantinas = [
        c for c in cantinas if safe_float(c.get("total_sales")) <= 0
    ]

    average_sales = (
        total_sales / len(active_cantinas)
        if active_cantinas
        else 0
    )

    weak_cantinas = []

    for cantina in active_cantinas:
        sales = safe_float(cantina.get("total_sales"))

        if average_sales > 0 and sales < average_sales * 0.4:
            weak_cantinas.append({
                "id": cantina.get("id"),
                "name": cantina.get("name"),
                "code": cantina.get("code"),
                "sales": round(sales, 2),
                "average_reference": round(average_sales, 2),
            })

    best_cantina = None
    worst_cantina = None

    if cantinas:
        best_cantina = max(
            cantinas,
            key=lambda c: safe_float(c.get("total_sales")),
        )

        worst_cantina = min(
            cantinas,
            key=lambda c: safe_float(c.get("total_sales")),
        )

    return {
        "total_cantinas": len(cantinas),
        "active_cantinas_count": len(active_cantinas),
        "inactive_cantinas_count": len(inactive_cantinas),
        "average_sales_per_active_cantina": round(average_sales, 2),
        "best_cantina": best_cantina,
        "worst_cantina": worst_cantina,
        "weak_cantinas": weak_cantinas,
        "inactive_cantinas": inactive_cantinas,
    }