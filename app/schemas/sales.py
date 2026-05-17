from pydantic import BaseModel
from typing import Optional, List


class SaleInput(BaseModel):
    id: str
    product_id: str
    product_name: str
    category: Optional[str] = None
    cantina_id: Optional[str] = None
    cantina_name: Optional[str] = None
    quantity: float
    unit_price: float
    unit_cost: float = 0
    total_amount: float
    sale_date: str


class SalesAnalysisInput(BaseModel):
    company_id: str
    currency: str = "AOA"
    lang: str = "pt"
    sales: List[SaleInput]