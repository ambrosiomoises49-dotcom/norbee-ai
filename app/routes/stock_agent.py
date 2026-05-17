from fastapi import APIRouter
from app.schemas.analysis import BusinessAnalysisInput
from app.agents.stock_agent import analyze_stock_agent

router = APIRouter()


@router.post("/")
def stock_agent(payload: BusinessAnalysisInput):
    return analyze_stock_agent(
        products=payload.products,
        lang=payload.lang,
    )