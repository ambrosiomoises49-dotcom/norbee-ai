def calculate_global_risk(stock_result: dict, sales_result: dict, finance_result: dict):
    score = 0

    critical_stock = len([
        alert for alert in stock_result.get("alerts", [])
        if getattr(alert, "level", None) == "critical"
        or alert.get("level") == "critical"
    ])

    high_stock = len([
        alert for alert in stock_result.get("alerts", [])
        if getattr(alert, "level", None) == "high"
        or alert.get("level") == "high"
    ])

    if critical_stock > 0:
        score += 40

    if high_stock > 0:
        score += 25

    if finance_result.get("balance", 0) < 0:
        score += 25

    if sales_result.get("total_revenue", 0) == 0:
        score += 10

    if score >= 70:
        level = "critical"
    elif score >= 45:
        level = "high"
    elif score >= 25:
        level = "medium"
    else:
        level = "low"

    return {
        "score": min(score, 100),
        "level": level,
    }


def generate_priorities(stock_result: dict, sales_result: dict, finance_result: dict):
    priorities = []

    for alert in stock_result.get("alerts", []):
        level = alert.level if hasattr(alert, "level") else alert.get("level")
        title = alert.title if hasattr(alert, "title") else alert.get("title")
        message = alert.message if hasattr(alert, "message") else alert.get("message")

        if level in ["critical", "high"]:
            priorities.append({
                "domain": "stock",
                "level": level,
                "title": title,
                "message": message,
            })

    if finance_result.get("balance", 0) < 0:
        priorities.append({
            "domain": "finance",
            "level": "high",
            "title": "Solde financier négatif",
            "message": "Les dépenses dépassent les entrées. Une action financière est nécessaire.",
        })

    if sales_result.get("total_revenue", 0) == 0:
        priorities.append({
            "domain": "sales",
            "level": "medium",
            "title": "Aucune vente détectée",
            "message": "Aucune vente n’a été détectée dans les données fournies.",
        })

    level_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    priorities.sort(key=lambda item: level_order.get(item["level"], 9))

    return priorities[:10]


def generate_executive_summary(risk: dict, priorities: list[dict]):
    if risk["level"] == "critical":
        return "La situation globale exige une intervention immédiate."

    if risk["level"] == "high":
        return "La situation présente plusieurs risques importants à traiter rapidement."

    if risk["level"] == "medium":
        return "La situation est globalement contrôlée, mais certains points doivent être surveillés."

    return "La situation générale semble stable."