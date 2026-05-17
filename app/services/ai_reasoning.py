def generate_reasoning(orchestrator_result: dict, memory_summary: dict):
    priorities = orchestrator_result.get("priorities", [])
    global_risk = orchestrator_result.get("global_risk", {})
    recommendations = orchestrator_result.get("recommendations", [])

    reasoning = {
        "main_explanation": "",
        "risk_interpretation": "",
        "priority_explanation": [],
        "recommendation_explanation": [],
    }

    risk_level = global_risk.get("level", "low")

    if risk_level == "critical":
        reasoning["main_explanation"] = (
            "L’IA considère que la situation globale est critique, "
            "car plusieurs indicateurs importants présentent des risques élevés."
        )
    elif risk_level == "high":
        reasoning["main_explanation"] = (
            "L’IA détecte une situation à surveiller de près. "
            "Certains indicateurs montrent des anomalies ou des risques importants."
        )
    else:
        reasoning["main_explanation"] = (
            "La situation globale semble relativement stable, "
            "mais certains points peuvent encore être optimisés."
        )

    reasoning["risk_interpretation"] = (
        f"Niveau de risque global détecté : {risk_level}."
    )

    for priority in priorities:
        reasoning["priority_explanation"].append({
            "title": priority.get("title"),
            "reason": (
                f"Cette priorité a été retenue car elle concerne le domaine "
                f"{priority.get('domain', 'général')} avec un niveau "
                f"{priority.get('level', 'moyen')}."
            ),
        })

    for recommendation in recommendations:
        reasoning["recommendation_explanation"].append({
            "recommendation": recommendation,
            "reason": (
                "Cette recommandation vise à améliorer la performance, "
                "réduire les risques ou optimiser la gestion."
            ),
        })

    if memory_summary.get("count", 0) > 0:
        reasoning["memory_context"] = (
            f"L’IA dispose déjà de {memory_summary.get('count')} analyses "
            "précédentes pour cette entreprise."
        )
    else:
        reasoning["memory_context"] = (
            "Aucune mémoire historique n’est encore disponible."
        )

    return reasoning