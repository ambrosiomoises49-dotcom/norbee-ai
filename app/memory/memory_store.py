import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path("data/ai_memory.json")


def _ensure_memory_file():
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("[]", encoding="utf-8")


def _load_memory() -> list[dict]:
    _ensure_memory_file()

    with MEMORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_memory(records: list[dict]):
    _ensure_memory_file()

    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def save_analysis(company_id: str, analysis: dict):
    records = _load_memory()

    record = {
        "company_id": company_id,
        "created_at": datetime.utcnow().isoformat(),
        "analysis": analysis,
    }

    records.append(record)
    _save_memory(records)

    return record


def get_company_memory(company_id: str, limit: int = 10):
    records = [
        item for item in _load_memory()
        if item["company_id"] == company_id
    ]

    return records[-limit:]


def compare_with_previous(company_id: str, current_risk_score: int):
    records = get_company_memory(company_id, limit=2)

    if len(records) < 2:
        return {
            "has_previous": False,
            "message": "Aucune analyse précédente disponible.",
        }

    previous_score = records[-2]["analysis"]["global_risk"]["score"]
    difference = current_risk_score - previous_score

    if difference > 0:
        trend = "worsening"
        message = f"Le risque global a augmenté de {difference} point(s)."
    elif difference < 0:
        trend = "improving"
        message = f"Le risque global a diminué de {abs(difference)} point(s)."
    else:
        trend = "stable"
        message = "Le risque global est stable."

    return {
        "has_previous": True,
        "previous_score": previous_score,
        "current_score": current_risk_score,
        "difference": difference,
        "trend": trend,
        "message": message,
    }