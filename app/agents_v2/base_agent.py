from typing import Any, Dict, List


def build_agent_result(
    agent: str,
    status: str = "ok",
    summary: str = "",
    signals: List[Dict[str, Any]] | None = None,
    risks: List[Dict[str, Any]] | None = None,
    decisions: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    return {
        "agent": agent,
        "status": status,
        "summary": summary,
        "signals": signals or [],
        "risks": risks or [],
        "decisions": decisions or [],
    }


def signal(
    name: str,
    value: Any,
    level: str = "info",
    explanation: str = "",
) -> Dict[str, Any]:
    return {
        "name": name,
        "value": value,
        "level": level,
        "explanation": explanation,
    }


def risk(
    risk_type: str,
    level: str,
    title: str,
    explanation: str,
) -> Dict[str, Any]:
    return {
        "type": risk_type,
        "level": level,
        "title": title,
        "explanation": explanation,
    }


def decision(
    decision_type: str,
    priority: str,
    title: str,
    action: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "type": decision_type,
        "priority": priority,
        "title": title,
        "action": action,
        "reason": reason,
    }