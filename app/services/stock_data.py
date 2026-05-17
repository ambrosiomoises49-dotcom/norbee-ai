import pandas as pd
from app.database.db import engine


def load_stock_products(company_id: str):
    query = """
        SELECT 
            p.id,
            p.name,
            p."internalCode",
            COALESCE(cs.quantity, 0) AS stock
        FROM "Product" p
        LEFT JOIN "CentralStock" cs ON cs."productId" = p.id
        WHERE p."companyId" = %(company_id)s
          AND p.status = 'ACTIVE'
    """

    return pd.read_sql(query, engine, params={"company_id": company_id})


def load_daily_sales(company_id: str):
    query = """
        SELECT
            si."productId",
            DATE(s."createdAt") AS day,
            SUM(si.quantity) AS quantity
        FROM "SaleItem" si
        JOIN "Sale" s ON s.id = si."saleId"
        WHERE s."companyId" = %(company_id)s
          AND s.status = 'COMPLETED'
        GROUP BY si."productId", DATE(s."createdAt")
        ORDER BY day ASC
    """

    return pd.read_sql(query, engine, params={"company_id": company_id})


def build_stock_dataset(company_id: str):
    products = load_stock_products(company_id)
    sales = load_daily_sales(company_id)

    dataset = []

    for _, product in products.iterrows():
      product_sales = sales[sales["productId"] == product["id"]]

      dataset.append({
          "id": product["id"],
          "name": product["name"],
          "internalCode": product["internalCode"],
          "stock": int(product["stock"]),
          "daily_sales": product_sales["quantity"].astype(float).tolist(),
      })

    return dataset