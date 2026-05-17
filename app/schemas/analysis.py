from pydantic import BaseModel
from typing import List, Optional


class ProductInput(BaseModel):
    id: str
    name: str
    internal_code: str
    category: Optional[str] = None
    current_stock: float = 0
    min_stock: float = 0
    purchase_price: float = 0
    sale_price: float = 0
    sales_last_7_days: float = 0
    sales_last_30_days: float = 0


class BusinessAnalysisInput(BaseModel):
    company_id: str
    currency: str = "AOA"
    lang: str = "pt"
    products: List[ProductInput] = []


class AlertOutput(BaseModel):
    level: str
    title: str
    message: str
    product_id: Optional[str] = None
    risk_score: Optional[int] = None
    days_until_stockout: Optional[float] = None
    recommended_reorder_quantity: Optional[float] = None
    estimated_lost_revenue: Optional[float] = None


class BusinessAnalysisOutput(BaseModel):
    summary: str
    alerts: List[AlertOutput]
    recommendations: List[str]