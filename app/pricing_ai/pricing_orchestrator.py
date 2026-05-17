from typing import Any, Dict

from app.pricing_ai.pricing_engine import build_pricing_recommendations


def run_pricing_ai(
    rich_dataset: Dict[str, Any],
    feature_store: Dict[str, Any],
) -> Dict[str, Any]:
    pricing_recommendations = build_pricing_recommendations(
        rich_dataset=rich_dataset,
        feature_store=feature_store,
    )

    return {
        "engine": "pricing_ai_v1",
        "pricing_recommendations": pricing_recommendations,
    }