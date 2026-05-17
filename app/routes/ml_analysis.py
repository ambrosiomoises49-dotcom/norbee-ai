from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.ml.sales_forecast import simple_sales_forecast
from app.ml.anomaly_detection import detect_anomalies
from app.ml.risk_score import calculate_ml_risk_score
from app.ml.trend_analysis import analyze_trend
from fastapi import APIRouter, Depends
from app.core.security import verify_api_key

router = APIRouter()

@router.post("/ml-analysis", dependencies=[Depends(verify_api_key)])

class MLAnalysisInput(BaseModel):
    company_id: str
    sales_history: List[float] = []
    profit_history: List[float] = []
    stock_history: List[float] = []
    periods: int = 7


@router.post("/ml-analysis")
async def ml_analysis(payload: MLAnalysisInput):
    sales_forecast = simple_sales_forecast(
        history=payload.sales_history,
        periods=payload.periods,
    )

    profit_forecast = simple_sales_forecast(
        history=payload.profit_history,
        periods=payload.periods,
    )

    sales_trend_analysis = analyze_trend(payload.sales_history)
    profit_trend_analysis = analyze_trend(payload.profit_history)

    sales_anomalies = detect_anomalies(payload.sales_history)
    profit_anomalies = detect_anomalies(payload.profit_history)
    stock_anomalies = detect_anomalies(payload.stock_history)

    risk_score = calculate_ml_risk_score(
        sales_trend=sales_forecast["trend"],
        profit_trend=profit_forecast["trend"],
        sales_anomalies=sales_anomalies["anomalies"],
        profit_anomalies=profit_anomalies["anomalies"],
        stock_anomalies=stock_anomalies["anomalies"],
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
            "A tendência histórica das vendas mostra queda. Comparar os períodos e identificar produtos com menor rotação."
        )

    if profit_trend_analysis["trend"] in ["decline", "strong_decline"]:
        recommendations.append(
            "A tendência histórica do lucro mostra degradação. Rever margens, custos fixos e despesas extraordinárias."
        )

    if sales_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias nas vendas. Verificar dias com valores muito diferentes do normal."
        )

    if profit_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias no lucro. Investigar custos extraordinários ou queda de margem."
        )

    if stock_anomalies["anomalies"]:
        recommendations.append(
            "Foram detetadas anomalias no stock. Verificar entradas, saídas e possíveis erros de inventário."
        )

    if not recommendations:
        recommendations.append(
            "Nenhum risco crítico detetado pelos modelos ML nesta análise."
        )

    executive_summary = (
        f"Análise ML concluída. Nível global: {risk_score['label']}. "
        f"Tendência de vendas: {sales_forecast['trend']}. "
        f"Tendência de lucro: {profit_forecast['trend']}. "
        f"Evolução histórica das vendas: {sales_trend_analysis['message']} "
        f"Evolução histórica do lucro: {profit_trend_analysis['message']}"
    )

    return {
        "agent": "ml_analysis",
        "status": "ok",
        "company_id": payload.company_id,
        "executive_summary": executive_summary,
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
        },
        "recommendations": recommendations,
    }