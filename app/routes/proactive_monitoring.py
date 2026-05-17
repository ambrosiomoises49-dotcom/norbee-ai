from fastapi import APIRouter, Depends, Query

from app.core.security import verify_api_key

from app.services.ml_dataset import build_ml_dataset
from app.services.rich_dataset import build_rich_company_dataset

from app.feature_store.company_feature_store import build_company_feature_store

from app.ml.forecast_engine_v2 import hybrid_forecast
from app.ml.anomaly_detection import detect_anomalies
from app.ml.advanced_anomaly import detect_advanced_anomalies
from app.ml.trend_analysis import analyze_trend
from app.ml.risk_score import calculate_ml_risk_score

from app.decision.advanced_decision_engine import generate_advanced_decisions

from app.memory.ml_memory import compare_with_last_ml_analysis

from app.proactive.proactive_monitoring_v2 import generate_proactive_monitoring

router = APIRouter()


@router.get(
    "/proactive-monitoring/{company_id}",
    dependencies=[Depends(verify_api_key)],
)
async def proactive_monitoring(
    company_id: str,
    days: int = Query(default=30, ge=7, le=365),
    periods: int = Query(default=30, ge=1, le=90),
):
    dataset = build_ml_dataset(company_id=company_id, days=days)

    if not dataset.get("exists", True):
        return {
            "agent": "proactive_monitoring",
            "status": "not_found",
            "company_id": company_id,
            "message": "Empresa não encontrada.",
        }

    rich_dataset = build_rich_company_dataset(company_id=company_id, days=days)

    feature_store = build_company_feature_store(
        dataset=rich_dataset,
        ml_dataset=dataset,
    )

    sales_history = dataset["sales_history"]
    profit_history = dataset["profit_history"]
    stock_history = dataset["stock_history"]

    sales_forecast = hybrid_forecast(history=sales_history, periods=periods)
    profit_forecast = hybrid_forecast(history=profit_history, periods=periods)

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

    current_analysis = {
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
        "decisions": decisions,
    }

    memory = compare_with_last_ml_analysis(
        company_id=company_id,
        current_analysis=current_analysis,
    )

    monitoring = generate_proactive_monitoring(
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
        memory=memory,
    )

    return {
        "agent": "proactive_monitoring",
        "status": "ok",
        "company_id": company_id,
        "risk_score": risk_score,
        "feature_store": feature_store,
        "forecast": {
            "sales": sales_forecast,
            "profit": profit_forecast,
        },
        "memory": memory,
        "monitoring": monitoring,
        "alerts": monitoring["alerts"],
        "summary": {
            "total_alerts": monitoring["total_alerts"],
            "high_count": monitoring["high_count"],
            "medium_count": monitoring["medium_count"],
        },
    }