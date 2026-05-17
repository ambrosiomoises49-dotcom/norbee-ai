from fastapi import APIRouter

from app.schemas.analysis import BusinessAnalysisInput, BusinessAnalysisOutput
from app.services.stock_forecasting import forecast_stock_risk
from app.utils.i18n import t

router = APIRouter()


@router.post("/", response_model=BusinessAnalysisOutput)
def stock_forecast(payload: BusinessAnalysisInput):
    alerts = forecast_stock_risk(payload.products, payload.lang)

    critical_count = len([a for a in alerts if a.level == "critical"])
    high_count = len([a for a in alerts if a.level == "high"])

    recommendations: list[str] = []

    if critical_count > 0:
        recommendations.append(t("order_critical_products", payload.lang))

    if high_count > 0:
        recommendations.append(t("plan_fast_restock", payload.lang))

    if not alerts:
        recommendations.append(t("stock_stable", payload.lang))

    summary = t(
        "analysis_summary",
        payload.lang,
        count=len(payload.products),
        alerts=len(alerts),
        critical=critical_count,
    )

    return BusinessAnalysisOutput(
        summary=summary,
        alerts=alerts,
        recommendations=recommendations,
    )