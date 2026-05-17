from typing import Any, Dict, List


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def build_step(
    level: str,
    step_type: str,
    title: str,
    explanation: str,
    action: str,
    evidence: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "level": level,
        "type": step_type,
        "title": title,
        "explanation": explanation,
        "action": action,
        "evidence": evidence or {},
    }


def reason_from_feature_store(
    question: str,
    feature_store: Dict[str, Any],
    dataset: Dict[str, Any],
    ml_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    q = question.lower()

    sales = feature_store.get("sales", {})
    stock = feature_store.get("stock", {})
    finance = feature_store.get("finance", {})
    cantinas = feature_store.get("cantinas", {})
    forecasting = feature_store.get("forecasting", {})

    steps: List[Dict[str, Any]] = []

    profit_margin = safe_float(sales.get("profit_margin_rate"))
    operating_ratio = safe_float(finance.get("operating_ratio"))
    cashflow = safe_float(finance.get("cashflow_estimation"))
    stock_health = safe_float(stock.get("stock_health_score"))
    sales_growth = safe_float(forecasting.get("sales_growth_rate"))
    profit_growth = safe_float(forecasting.get("profit_growth_rate"))
    sales_volatility = safe_float(forecasting.get("sales_volatility"))

    if profit_margin < 15:
        steps.append(
            build_step(
                level="high",
                step_type="weak_margin",
                title="Marge globale faible",
                explanation=(
                    f"La marge estimée est de {profit_margin:.2f}%, ce qui indique "
                    "une rentabilité fragile."
                ),
                action=(
                    "Identifier les produits à faible marge, revoir les prix de vente "
                    "et négocier les coûts d’achat."
                ),
                evidence={"profit_margin_rate": profit_margin},
            )
        )

    if operating_ratio > 75:
        steps.append(
            build_step(
                level="high",
                step_type="high_cost_pressure",
                title="Pression élevée des coûts",
                explanation=(
                    f"Les coûts représentent environ {operating_ratio:.2f}% du chiffre d’affaires."
                ),
                action=(
                    "Auditer les coûts principaux, réduire les dépenses non essentielles "
                    "et renégocier les fournisseurs."
                ),
                evidence={"operating_ratio": operating_ratio},
            )
        )

    if cashflow < 0:
        steps.append(
            build_step(
                level="high",
                step_type="negative_cashflow",
                title="Cashflow estimé négatif",
                explanation=(
                    f"Le cashflow estimé est de {cashflow:.2f}. "
                    "L’entreprise sort plus d’argent qu’elle n’en génère sur la période."
                ),
                action=(
                    "Réduire les dépenses immédiates, accélérer les ventes et limiter "
                    "les achats non urgents."
                ),
                evidence={"cashflow_estimation": cashflow},
            )
        )

    if stock_health < 70:
        critical_products = stock.get("critical_products", [])

        steps.append(
            build_step(
                level="high",
                step_type="stock_health_low",
                title="Santé du stock faible",
                explanation=(
                    f"Le score de santé du stock est de {stock_health:.0f}/100. "
                    f"{len(critical_products)} produit(s) sont critiques."
                ),
                action=(
                    "Réapprovisionner les produits critiques et surveiller les ruptures "
                    "dans les prochains jours."
                ),
                evidence={"critical_products": critical_products[:5]},
            )
        )

    if sales_growth < -20:
        steps.append(
            build_step(
                level="high",
                step_type="sales_decline",
                title="Forte baisse des ventes",
                explanation=(
                    f"La croissance des ventes est de {sales_growth:.2f}%, "
                    "ce qui indique une baisse forte sur la période."
                ),
                action=(
                    "Identifier les produits et cantinas responsables de la baisse, "
                    "puis lancer une action commerciale ciblée."
                ),
                evidence={"sales_growth_rate": sales_growth},
            )
        )

    if profit_growth < -20:
        steps.append(
            build_step(
                level="high",
                step_type="profit_decline",
                title="Forte baisse du bénéfice",
                explanation=(
                    f"La croissance du bénéfice est de {profit_growth:.2f}%, "
                    "ce qui indique une dégradation importante."
                ),
                action=(
                    "Analyser marges, coûts et produits à faible rentabilité pour restaurer "
                    "le bénéfice."
                ),
                evidence={"profit_growth_rate": profit_growth},
            )
        )

    if sales_volatility > 80:
        steps.append(
            build_step(
                level="medium",
                step_type="sales_instability",
                title="Ventes instables",
                explanation=(
                    f"La volatilité des ventes est élevée ({sales_volatility:.2f}%). "
                    "L’activité est irrégulière."
                ),
                action=(
                    "Étudier les jours de forte baisse et de forte hausse pour comprendre "
                    "les facteurs saisonniers ou opérationnels."
                ),
                evidence={"sales_volatility": sales_volatility},
            )
        )

    weak_cantinas = cantinas.get("weak_cantinas", [])
    inactive_cantinas = cantinas.get("inactive_cantinas", [])

    if weak_cantinas:
        steps.append(
            build_step(
                level="medium",
                step_type="weak_cantinas",
                title="Cantinas faibles détectées",
                explanation=(
                    f"{len(weak_cantinas)} cantina(s) ont des ventes très inférieures "
                    "à la moyenne."
                ),
                action=(
                    "Auditer ces cantinas : stock disponible, personnel, emplacement, "
                    "heures d’ouverture et saisie des ventes."
                ),
                evidence={"weak_cantinas": weak_cantinas[:5]},
            )
        )

    if inactive_cantinas:
        steps.append(
            build_step(
                level="medium",
                step_type="inactive_cantinas",
                title="Cantinas sans ventes",
                explanation=(
                    f"{len(inactive_cantinas)} cantina(s) n’ont généré aucune vente."
                ),
                action=(
                    "Vérifier si ces cantinas sont réellement ouvertes, correctement alimentées "
                    "en stock et bien configurées."
                ),
                evidence={"inactive_cantinas": inactive_cantinas[:5]},
            )
        )

    if not steps:
        steps.append(
            build_step(
                level="low",
                step_type="stable_business",
                title="Situation globalement stable",
                explanation=(
                    "Les principaux indicateurs ne montrent pas de risque critique immédiat."
                ),
                action=(
                    "Continuer le suivi quotidien des ventes, du stock et de la marge."
                ),
                evidence={},
            )
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}

    steps = sorted(
        steps,
        key=lambda item: priority_order.get(item["level"], 3),
    )

    answer_lines = [
        "Voici mon raisonnement basé sur les signaux avancés de l’entreprise :",
        "",
    ]

    for index, step in enumerate(steps[:6], start=1):
        answer_lines.append(
            f"{index}. {step['title']} — {step['explanation']}"
        )

    answer_lines.append("")
    answer_lines.append("Décisions recommandées :")

    for index, step in enumerate(steps[:6], start=1):
        answer_lines.append(f"{index}. {step['action']}")

    return {
        "engine": "reasoning_engine_v3",
        "answer": "\n".join(answer_lines),
        "reasoning_steps": steps,
        "decisions": [
            {
                "priority": step["level"],
                "type": step["type"],
                "title": step["title"],
                "reason": step["explanation"],
                "action": step["action"],
                "evidence": step["evidence"],
            }
            for step in steps
        ],
    }