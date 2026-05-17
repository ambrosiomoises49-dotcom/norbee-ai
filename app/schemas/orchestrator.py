from typing import List
from pydantic import BaseModel

from app.schemas.analysis import ProductInput
from app.schemas.sales import SaleInput
from app.schemas.finance import FinanceTransactionInput


class OrchestratorInput(BaseModel):
    company_id: str
    currency: str = "AOA"
    lang: str = "pt"
    question: str | None = None
    products: List[ProductInput] = []
    sales: List[SaleInput] = []
    transactions: List[FinanceTransactionInput] = []