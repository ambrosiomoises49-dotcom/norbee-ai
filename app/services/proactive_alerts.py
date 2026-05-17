from datetime import datetime


def generate_proactive_alerts(orchestrator_result: dict):
    alerts = []

    priorities = orchestrator_result.get("priorities", [])
    global_risk = orchestrator_result.get("global_risk", {})

    for priority in priorities:
        alerts.append({
            "type": "priority_alert",
            "notification_type": priority.get("domain", "AI"),
            "level": priority.get("level", "medium"),
            "title": priority.get("title"),
            "message": priority.get("message"),
            "domain": priority.get("domain"),
            "created_at": datetime.utcnow().isoformat(),
        })

    risk_level = global_risk.get("level")

    if risk_level == "critical":
        alerts.append({
            "type": "global_risk",
            "notification_type": "AI",
            "level": "critical",
            "title": "Risque global critique",
            "message": (
                "L’entreprise présente plusieurs risques importants "
                "nécessitant une intervention immédiate."
            ),
            "created_at": datetime.utcnow().isoformat(),
        })

    elif risk_level == "high":
        alerts.append({
            "type": "global_risk",
            "notification_type": "AI",
            "level": "high",
            "title": "Risque global élevé",
            "message": "Plusieurs anomalies importantes ont été détectées.",
            "created_at": datetime.utcnow().isoformat(),
        })

    return alerts