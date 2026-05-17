from typing import Any, Dict, List

from app.agents_v2.base_agent import build_agent_result, signal, risk, decision


def run_risk_agent_v2(
    agent_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    all_risks = []
    all_decisions = []

    for result in agent_results:
        all_risks.extend(result.get("risks", []))
        all_decisions.extend(result.get("decisions", []))

    high_risks = [r for r in all_risks if r.get("level") == "high"]
    medium_risks = [r for r in all_risks if r.get("level") == "medium"]

    score = min((len(high_risks) * 25) + (len(medium_risks) * 10), 100)

    if score >= 70:
        level = "high"
        label = "Risque élevé"
    elif score >= 40:
        level = "medium"
        label = "Risque modéré"
    else:
        level = "low"
        label = "Risque faible"

    risks = []

    if high_risks:
        risks.append(
            risk(
                "global_high_risk",
                "high",
                "Risque global élevé",
                f"{len(high_risks)} risque(s) élevé(s) détecté(s).",
            )
        )

    decisions = []

    if level == "high":
        decisions.append(
            decision(
                "executive_review",
                "high",
                "Réunion de pilotage urgente",
                "Traiter les risques stock, ventes et finance dans les 24h.",
                "Le niveau global de risque est élevé.",
            )
        )

    return build_agent_result(
        agent="risk_agent_v2",
        summary=f"{label} avec score {score}/100.",
        signals=[
            signal("risk_score", score, level, "Score global de risque."),
            signal("high_risks_count", len(high_risks), "danger", "Nombre de risques élevés."),
            signal("medium_risks_count", len(medium_risks), "warning", "Nombre de risques moyens."),
        ],
        risks=risks,
        decisions=decisions,
    )