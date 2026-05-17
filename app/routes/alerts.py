from fastapi import APIRouter

from app.schemas.analysis import BusinessAnalysisInput, BusinessAnalysisOutput
from app.agents.stock_agent import analyze_stock
from app.agents.sales_agent import analyze_sales
from app.agents.finance_agent import analyze_finance

router = APIRouter()


@router.post("/analyze", response_model=BusinessAnalysisOutput)
async def analyze_business(data: BusinessAnalysisInput):
    stock_alerts = analyze_stock(data.products)

    recommendations = []

    for alert in stock_alerts:
        if alert.recommended_reorder_quantity:
            recommendations.append(
                f"Repor aproximadamente {alert.recommended_reorder_quantity:.0f} unidades de {alert.title.replace('Stock baixo: ', '')}."
            )

    summary = (
        "Análise concluída. Foram detetados riscos de stock."
        if stock_alerts
        else "Análise concluída. Nenhum risco crítico detetado."
    )

    return BusinessAnalysisOutput(
        summary=summary,
        alerts=stock_alerts,
        recommendations=recommendations,
    )