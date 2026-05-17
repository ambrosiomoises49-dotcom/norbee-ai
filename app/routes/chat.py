from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import verify_api_key

from app.services.rich_dataset import build_rich_company_dataset
from app.services.ml_dataset import build_ml_dataset

from app.feature_store.company_feature_store import build_company_feature_store

from app.ml.forecast_engine_v2 import hybrid_forecast

from app.ai.reasoning_engine import classify_question
from app.ai.reasoning_engine_v3 import reason_from_feature_store

from app.agents_v2.orchestrator_v2 import run_orchestrator_v2


router = APIRouter()


class ChatInput(BaseModel):
    company_id: str
    question: str
    lang: str = "pt"
    days: int = 30


@router.post("/chat", dependencies=[Depends(verify_api_key)])
async def ai_chat(payload: ChatInput):
    dataset = build_rich_company_dataset(
        company_id=payload.company_id,
        days=payload.days,
    )

    if not dataset.get("exists", True):
        return {
            "agent": "chat",
            "status": "not_found",
            "company_id": payload.company_id,
            "question": payload.question,
            "answer": "Empresa não encontrada.",
            "recommendations": [],
            "decisions": [],
        }

    ml_dataset = build_ml_dataset(
        company_id=payload.company_id,
        days=payload.days,
    )

    feature_store = build_company_feature_store(
        dataset=dataset,
        ml_dataset=ml_dataset,
    )

    sales_history = ml_dataset.get("sales_history", [])
    profit_history = ml_dataset.get("profit_history", [])

    sales_forecast = hybrid_forecast(
        history=sales_history,
        periods=30,
    )

    profit_forecast = hybrid_forecast(
        history=profit_history,
        periods=30,
    )

    forecast_payload = {
        "sales": sales_forecast,
        "profit": profit_forecast,
    }

    multi_agent = run_orchestrator_v2(
        feature_store=feature_store,
        rich_dataset=dataset,
        forecast=forecast_payload,
    )

    classification = classify_question(payload.question)

    reasoning_result = reason_from_feature_store(
        question=payload.question,
        feature_store=feature_store,
        dataset=dataset,
        ml_dataset=ml_dataset,
    )

    decisions = reasoning_result.get("decisions", [])

    executive_decisions = multi_agent.get("executive_decisions", [])

    all_recommendations = [
        decision.get("action", "")
        for decision in decisions
        if decision.get("action")
    ]

    for decision in executive_decisions:
        action = decision.get("action")

        if action and action not in all_recommendations:
            all_recommendations.append(action)

    return {
        "agent": "chat",
        "status": "ok",
        "company_id": payload.company_id,
        "question": payload.question,
        "intent": classification["main_intent"],
        "intents": classification["intents"],
        "reasoning_engine": reasoning_result.get("engine"),
        "answer": reasoning_result["answer"],
        "reasoning_steps": reasoning_result["reasoning_steps"],
        "decisions": decisions,
        "recommendations": all_recommendations,
        "forecast": forecast_payload,
        "feature_store": feature_store,
        "multi_agent": multi_agent,
        "executive_decisions": executive_decisions,
        "context": {
            "days": payload.days,
            "stock_risks_count": len(dataset.get("stock_risks", [])),
            "products_analyzed": len(dataset.get("sales_by_product", [])),
            "cantinas_analyzed": len(dataset.get("sales_by_cantina", [])),
        },
    }