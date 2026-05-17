from pydantic import BaseModel
from typing import Optional, List


class FinanceTransactionInput(BaseModel):
    id: str
    type: str
    amount: float
    description: Optional[str] = None
    category: Optional[str] = None
    reference_type: Optional[str] = None
    date: str


class FinanceAnalysisInput(BaseModel):
    company_id: str
    currency: str = "AOA"
    lang: str = "pt"
    transactions: List[FinanceTransactionInput]