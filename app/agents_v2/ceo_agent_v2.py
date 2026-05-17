from typing import Any, Dict, List

from app.agents_v2.base_agent import build_agent_result, decision


def run_ceo_agent_v2(
    agent_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    decisions = []

    for result in agent_results:
        decisions.extend(result.get("decisions", []))

    priority_order = {"high": 0, "medium": 1, "low": 2}

    decisions = sorted(
        decisions,
        key=lambda d: priority_order.get(d.get("priority"), 3),
    )

    top_decisions = decisions[:8]

    summary_lines = []

    for result in agent_results:
        summary = result.get("summary")
        if summary:
            summary_lines.append(f"{result.get('agent')}: {summary}")

    executive_summary = " | ".join(summary_lines)

    if not top_decisions:
        top_decisions.append(
            decision(
                "daily_monitoring",
                "low",
                "Continuer le suivi",
                "Maintenir la surveillance quotidienne des ventes, stock et finance.",
                "Aucune action critique immédiate n’a été détectée.",
            )
        )

    return build_agent_result(
        agent="ceo_agent_v2",
        summary=executive_summary,
        decisions=top_decisions,
    )