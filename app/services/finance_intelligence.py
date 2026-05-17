from statistics import mean


def detect_financial_risks(finance_data: dict):
    alerts = []

    monthly_income = finance_data.get("monthly_income", [])
    monthly_expenses = finance_data.get("monthly_expenses", [])
    cash_balance = finance_data.get("cash_balance", 0)
    recent_costs = finance_data.get("recent_costs", [])

    if len(monthly_income) >= 3 and len(monthly_expenses) >= 3:
        avg_income = mean(monthly_income)
        avg_expense = mean(monthly_expenses)

        if avg_expense > avg_income * 0.85:
            alerts.append({
                "notification_type": "AI",
                "level": "high",
                "title": "Risque financier élevé",
                "message": (
                    "Les charges représentent plus de 85% des revenus moyens. "
                    "Une analyse des coûts est recommandée."
                ),
            })

    if cash_balance < 0:
        alerts.append({
            "notification_type": "AI",
            "level": "critical",
            "title": "Solde négatif",
            "message": (
                "Le solde financier global est négatif. "
                "Une action immédiate est nécessaire."
            ),
        })

    if len(recent_costs) >= 5:
        amounts = [float(cost.get("amount", 0)) for cost in recent_costs]
        avg_cost = mean(amounts)

        for cost in recent_costs:
            amount = float(cost.get("amount", 0))

            if amount > avg_cost * 2.5:
                alerts.append({
                    "notification_type": "AI",
                    "level": "medium",
                    "title": "Dépense inhabituelle détectée",
                    "message": (
                        f"La dépense '{cost.get('description', 'Sans description')}' "
                        f"semble anormalement élevée."
                    ),
                })

    return alerts