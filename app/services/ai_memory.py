from datetime import datetime


memory_store = {}


def save_memory(company_id: str, category: str, data: dict):
    if company_id not in memory_store:
        memory_store[company_id] = []

    memory_store[company_id].append({
        "category": category,
        "data": data,
        "created_at": datetime.utcnow().isoformat(),
    })

    return {
        "success": True,
        "message": "Memory saved",
    }


def get_memory(company_id: str):
    return memory_store.get(company_id, [])


def get_recent_memory(company_id: str, limit: int = 10):
    memories = memory_store.get(company_id, [])
    return memories[-limit:]


def summarize_memory(company_id: str):
    memories = memory_store.get(company_id, [])

    if not memories:
        return {
            "summary": "Aucune mémoire disponible pour cette entreprise.",
            "count": 0,
        }

    categories = {}

    for item in memories:
        category = item.get("category", "unknown")
        categories[category] = categories.get(category, 0) + 1

    return {
        "summary": "Mémoire IA disponible.",
        "count": len(memories),
        "categories": categories,
        "last_memory": memories[-1],
    }