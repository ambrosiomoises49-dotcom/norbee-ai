from typing import Any, Dict

from app.feature_store.sales_features import build_sales_features
from app.feature_store.stock_features import build_stock_features
from app.feature_store.finance_features import build_finance_features
from app.feature_store.cantina_features import build_cantina_features
from app.feature_store.forecasting_features import build_forecasting_features


def build_company_feature_store(
    dataset: Dict[str, Any],
    ml_dataset: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    sales_features = build_sales_features(dataset)
    stock_features = build_stock_features(dataset)
    finance_features = build_finance_features(dataset)
    cantina_features = build_cantina_features(dataset)

    forecasting_features = {}

    if ml_dataset:
        forecasting_features = build_forecasting_features(ml_dataset)

    return {
        "sales": sales_features,
        "stock": stock_features,
        "finance": finance_features,
        "cantinas": cantina_features,
        "forecasting": forecasting_features,
    }