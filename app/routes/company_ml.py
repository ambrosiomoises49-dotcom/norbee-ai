from fastapi import APIRouter, Depends, Query

from app.core.security import verify_api_key

from app.services.ml_dataset import build_ml_dataset
from app.services.rich_dataset import build_rich_company_dataset

from app.feature_store.company_feature_store import build_company_feature_store
from app.supply_ai.supply_orchestrator import run_supply_ai

from app.ml.forecast_engine_v2 import hybrid_forecast
from app.ml.anomaly_detection import detect_anomalies
from app.ml.advanced_anomaly import detect_advanced_anomalies
from app.ml.risk_score import calculate_ml_risk_score
from app.ml.trend_analysis import analyze_trend
from app.agents_v2.orchestrator_v2 import run_orchestrator_v2
from app.pricing_ai.pricing_orchestrator import run_pricing_ai

from app.decision.advanced_decision_engine import generate_advanced_decisions

from app.memory.ml_memory import (
    compare_with_last_ml_analysis,
    save_ml_analysis,
)

from app.proactive.proactive_monitoring_v2 import generate_proactive_monitoring


router = APIRouter()


@router.get(
    "/company-ml-analysis/{company_id}",
    dependencies=[Depends(verify_api_key)],
)
async def company_ml_analysis(
    company_id: str,
    days: int = Query(default=30, ge=7, le=365),
    periods: int = Query(default=7, ge=1, le=90),
):
    dataset = build_ml_dataset(
        company_id=company_id,
        days=days,
    )

    if not dataset.get("exists", True):
        return {
            "agent": "company_ml_analysis",
            "status": "not_found",
            "company_id": company_id,
            "message": "Empresa não encontrada.",
        }

    rich_dataset = build_rich_company_dataset(
        company_id=company_id,
        days=days,
    )
    supply_ai = run_supply_ai(
    rich_dataset=rich_dataset,
)

    feature_store = build_company_feature_store(
        dataset=rich_dataset,
        ml_dataset=dataset,
    )
    pricing_ai = run_pricing_ai(
    rich_dataset=rich_dataset,
    feature_store=feature_store,
)

    sales_history = dataset["sales_history"]
    profit_history = dataset["profit_history"]
    stock_history = dataset["stock_history"]

    sales_forecast = hybrid_forecast(
        history=sales_history,
        periods=periods,
    )

    profit_forecast = hybrid_forecast(
        history=profit_history,
        periods=periods,
    )
    forecast_payload = {
    "sales": sales_forecast,
    "profit": profit_forecast,
}

    sales_anomalies = detect_anomalies(sales_history)
    profit_anomalies = detect_anomalies(profit_history)
    stock_anomalies = detect_anomalies(stock_history)

    advanced_anomalies = detect_advanced_anomalies(rich_dataset)

    sales_trend_analysis = analyze_trend(sales_history)
    profit_trend_analysis = analyze_trend(profit_history)

    risk_score = calculate_ml_risk_score(
        sales_trend=sales_forecast["trend"],
        profit_trend=profit_forecast["trend"],
        sales_anomalies=sales_anomalies["anomalies"],
        profit_anomalies=profit_anomalies["anomalies"],
        stock_anomalies=stock_anomalies["anomalies"]
        + advanced_anomalies["anomalies"],
    )

    recommendations = []

    if sales_forecast["trend"] == "down":
        recommendations.append(
            "As vendas apresentam tendência de queda. Reforçar produtos mais vendidos e campanhas comerciais."
        )

    if profit_forecast["trend"] == "down":
        recommendations.append(
            "O lucro apresenta tendência de queda. Rever custos, margens e despesas operacionais."
        )

    if sales_trend_analysis["trend"] in ["decline", "strong_decline"]:
        recommendations.append(
            "A evolução histórica das vendas mostra queda. Identificar produtos e cantinas responsáveis."
        )

    if profit_trend_analysis["trend"] in ["decline", "strong_decline"]:
        recommendations.append(
            "A evolução histórica do lucro mostra degradação. Rever margens, despesas e custos fixos."
        )

    if sales_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias nas vendas. Verificar dias com valores fora do padrão."
        )

    if profit_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias no lucro. Investigar custos extraordinários ou queda de margem."
        )

    if stock_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias no stock. Verificar entradas, saídas e possíveis erros de inventário."
        )

    for anomaly in advanced_anomalies["anomalies"]:
        recommendation = anomaly.get("recommendation")

        if recommendation and recommendation not in recommendations:
            recommendations.append(recommendation)

    if not recommendations:
        recommendations.append(
            "Nenhum risco crítico detetado pelos modelos ML nesta análise."
        )

    decisions = generate_advanced_decisions(
        rich_dataset=rich_dataset,
        forecast={
            "sales": sales_forecast,
            "profit": profit_forecast,
        },
        trend_analysis={
            "sales": sales_trend_analysis,
            "profit": profit_trend_analysis,
        },
        anomalies={
            "sales": sales_anomalies,
            "profit": profit_anomalies,
            "stock": stock_anomalies,
            "advanced": advanced_anomalies,
        },
        risk_score=risk_score,
    )

    multi_agent = run_orchestrator_v2(
    feature_store=feature_store,
    rich_dataset=rich_dataset,
    forecast=forecast_payload,
)

    analysis_result = {
        "pricing_ai": pricing_ai,
        "supply_ai": supply_ai,
        "agent": "company_ml_analysis",
        "status": "ok",
        "company_id": company_id,
        "dataset": dataset,
        "rich_dataset": rich_dataset,
        "feature_store": feature_store,
        "executive_summary": (
            f"Análise ML automática concluída. "
            f"Nível global: {risk_score['label']}. "
            f"Tendência de vendas: {sales_forecast['trend']}. "
            f"Tendência de lucro: {profit_forecast['trend']}. "
            f"Anomalias avançadas detetadas: {advanced_anomalies['count']}."
        ),
        "risk_score": risk_score,
        "forecast": {
            "sales": sales_forecast,
            "profit": profit_forecast,
        },
        "trend_analysis": {
            "sales": sales_trend_analysis,
            "profit": profit_trend_analysis,
        },
        "anomalies": {
            "sales": sales_anomalies,
            "profit": profit_anomalies,
            "stock": stock_anomalies,
            "advanced": advanced_anomalies,
        },
        "recommendations": recommendations,
        "decisions": decisions,
        "multi_agent": multi_agent,
        "executive_decisions": multi_agent.get("executive_decisions", []),
    }

    memory_comparison = compare_with_last_ml_analysis(
        company_id=company_id,
        current_analysis=analysis_result,
    )

    analysis_result["memory"] = memory_comparison

    proactive_monitoring = generate_proactive_monitoring(
        feature_store=feature_store,
        forecast={
            "sales": sales_forecast,
            "profit": profit_forecast,
        },
        anomalies={
            "sales": sales_anomalies,
            "profit": profit_anomalies,
            "stock": stock_anomalies,
            "advanced": advanced_anomalies,
        },
        decisions=decisions,
        memory=memory_comparison,
    )

    analysis_result["proactive_monitoring"] = proactive_monitoring

    save_ml_analysis(
        company_id=company_id,
        analysis=analysis_result,
    )

    return analysis_result