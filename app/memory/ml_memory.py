import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


MEMORY_DIR = Path("storage/memory")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _memory_file(company_id: str) -> Path:
    safe_company_id = company_id.replace("/", "_").replace("\\", "_")
    return MEMORY_DIR / f"{safe_company_id}_ml_memory.json"


def load_ml_memory(company_id: str) -> List[Dict[str, Any]]:
    file_path = _memory_file(company_id)

    if not file_path.exists():
        return []

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_ml_analysis(company_id: str, analysis: Dict[str, Any]) -> None:
    memory = load_ml_memory(company_id)

    snapshot = {
        "created_at": datetime.utcnow().isoformat(),
        "risk_score": analysis.get("risk_score", {}),
        "forecast": analysis.get("forecast", {}),
        "trend_analysis": analysis.get("trend_analysis", {}),
        "anomalies_count": analysis.get("anomalies", {})
        .get("advanced", {})
        .get("count", 0),
        "recommendations_count": len(analysis.get("recommendations", [])),
        "decisions_count": len(analysis.get("decisions", [])),
    }

    memory.append(snapshot)

    memory = memory[-50:]

    _memory_file(company_id).write_text(
        json.dumps(memory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def compare_with_last_ml_analysis(
    company_id: str,
    current_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    memory = load_ml_memory(company_id)

    if not memory:
        return {
            "status": "first_analysis",
            "message": "Primeira análise ML guardada. Ainda não há histórico para comparação.",
            "previous_risk_score": None,
            "current_risk_score": current_analysis.get("risk_score", {}).get("score", 0),
            "risk_evolution": "unknown",
        }

    previous = memory[-1]

    previous_score = previous.get("risk_score", {}).get("score", 0)
    current_score = current_analysis.get("risk_score", {}).get("score", 0)

    diff = current_score - previous_score

    if diff > 5:
        evolution = "increased"
        message = "O risco aumentou desde a última análise."
    elif diff < -5:
        evolution = "decreased"
        message = "O risco diminuiu desde a última análise."
    else:
        evolution = "stable"
        message = "O risco manteve-se relativamente estável."

    previous_anomalies = previous.get("anomalies_count", 0)
    current_anomalies = (
        current_analysis.get("anomalies", {})
        .get("advanced", {})
        .get("count", 0)
    )

    return {
        "status": "ok",
        "message": message,
        "previous_risk_score": previous_score,
        "current_risk_score": current_score,
        "risk_difference": diff,
        "risk_evolution": evolution,
        "previous_anomalies_count": previous_anomalies,
        "current_anomalies_count": current_anomalies,
        "anomalies_difference": current_anomalies - previous_anomalies,
    }