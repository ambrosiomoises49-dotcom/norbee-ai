from typing import Any, Dict

from app.schemas.orchestrator import OrchestratorInput

from app.agents.stock_agent import analyze_stock
from app.agents.sales_agent import analyze_sales_agent
from app.agents.finance_agent import analyze_finance_agent

from app.decision.decision_engine import (
    calculate_global_risk,
    generate_priorities,
    generate_executive_summary,
)

from app.memory.memory_store import save_analysis, compare_with_previous


def run_orchestrator(payload: OrchestratorInput) -> Dict[str, Any]:
    stock_alerts = analyze_stock(payload.products)

    stock_result = {
        "agent": "stock_agent",
        "status": "ok",
        "alerts": [alert.model_dump() for alert in stock_alerts],
        "alerts_count": len(stock_alerts),
        "summary": (
            "Riscos de stock encontrados."
            if stock_alerts
            else "Nenhum risco crítico de stock encontrado."
        ),
    }

    sales_result = analyze_sales_agent(
        sales=payload.sales,
        lang=payload.lang,
    )

    finance_result = analyze_finance_agent(
        transactions=payload.transactions,
        lang=payload.lang,
    )

    global_risk = calculate_global_risk(
        stock_result=stock_result,
        sales_result=sales_result,
        finance_result=finance_result,
    )

    priorities = generate_priorities(
        stock_result=stock_result,
        sales_result=sales_result,
        finance_result=finance_result,
    )

    executive_summary = generate_executive_summary(
        risk=global_risk,
        priorities=priorities,
    )

    result = {
        "agent": "orchestrator",
        "status": "ok",
        "company_id": payload.company_id,
        "question": payload.question,
        "executive_summary": executive_summary,
        "global_risk": global_risk,
        "priorities": priorities,
        "stock": stock_result,
        "sales": sales_result,
        "finance": finance_result,
    }

    try:
        save_analysis(payload.company_id, result)

        trend = compare_with_previous(
            company_id=payload.company_id,
            current_risk_score=global_risk.get("score", 0),
        )

        result["trend"] = trend

    except Exception as error:
        result["trend"] = {
            "status": "unavailable",
            "message": "Memory comparison unavailable.",
            "error": str(error),
        }

    return result