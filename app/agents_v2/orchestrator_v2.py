from typing import Any, Dict

from app.agents_v2.sales_agent_v2 import run_sales_agent_v2
from app.agents_v2.finance_agent_v2 import run_finance_agent_v2
from app.agents_v2.stock_agent_v2 import run_stock_agent_v2
from app.agents_v2.forecast_agent_v2 import run_forecast_agent_v2
from app.agents_v2.risk_agent_v2 import run_risk_agent_v2
from app.agents_v2.ceo_agent_v2 import run_ceo_agent_v2


def run_orchestrator_v2(
    feature_store: Dict[str, Any],
    rich_dataset: Dict[str, Any],
    forecast: Dict[str, Any],
) -> Dict[str, Any]:
    sales_result = run_sales_agent_v2(
        feature_store=feature_store,
        rich_dataset=rich_dataset,
    )

    finance_result = run_finance_agent_v2(
        feature_store=feature_store,
        rich_dataset=rich_dataset,
    )

    stock_result = run_stock_agent_v2(
        feature_store=feature_store,
        rich_dataset=rich_dataset,
    )

    forecast_result = run_forecast_agent_v2(
        forecast=forecast,
        feature_store=feature_store,
    )

    first_layer = [
        sales_result,
        finance_result,
        stock_result,
        forecast_result,
    ]

    risk_result = run_risk_agent_v2(first_layer)

    second_layer = first_layer + [risk_result]

    ceo_result = run_ceo_agent_v2(second_layer)

    return {
        "engine": "multi_agent_orchestrator_v2",
        "agents": {
            "sales": sales_result,
            "finance": finance_result,
            "stock": stock_result,
            "forecast": forecast_result,
            "risk": risk_result,
            "ceo": ceo_result,
        },
        "executive_summary": ceo_result.get("summary"),
        "executive_decisions": ceo_result.get("decisions", []),
    }