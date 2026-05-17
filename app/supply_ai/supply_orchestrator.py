from typing import Any, Dict

from app.supply_ai.stock_rotation_engine import analyze_stock_rotation
from app.supply_ai.purchase_recommendation_engine import build_purchase_recommendations
from app.supply_ai.transfer_optimization_engine import build_transfer_recommendations


def run_supply_ai(
    rich_dataset: Dict[str, Any],
) -> Dict[str, Any]:
    stock_rotation = analyze_stock_rotation(
        rich_dataset=rich_dataset,
    )

    purchase_recommendations = build_purchase_recommendations(
        stock_rotation=stock_rotation,
    )

    transfer_recommendations = build_transfer_recommendations(
        rich_dataset=rich_dataset,
    )

    return {
        "engine": "supply_ai_v1",
        "stock_rotation": stock_rotation,
        "purchase_recommendations": purchase_recommendations,
        "transfer_recommendations": transfer_recommendations,
    }