from fastapi import APIRouter
from app.schemas.finance import FinanceAnalysisInput
from app.agents.finance_agent import analyze_finance_agent

router = APIRouter()


@router.post("/")
def finance_agent(payload: FinanceAnalysisInput):
    return analyze_finance_agent(
        transactions=payload.transactions,
        lang=payload.lang,
    )
