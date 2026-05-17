from fastapi import APIRouter
from app.schemas.sales import SalesAnalysisInput
from app.agents.sales_agent import analyze_sales_agent

router = APIRouter()


@router.post("/")
def sales_agent(payload: SalesAnalysisInput):
    return analyze_sales_agent(
        sales=payload.sales,
        lang=payload.lang,
    )