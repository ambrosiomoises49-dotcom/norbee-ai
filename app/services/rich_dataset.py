from sqlalchemy import text
from app.database.database import engine


def build_rich_company_dataset(company_id: str, days: int = 30):
    with engine.connect() as conn:
        company = conn.execute(
            text(
                """
                SELECT id, name
                FROM "Company"
                WHERE id = :company_id
                LIMIT 1
                """
            ),
            {"company_id": company_id},
        ).fetchone()

        if not company:
            return {"exists": False, "company_id": company_id}

        sales_by_cantina = conn.execute(
            text(
                """
                SELECT 
                    c.id,
                    c.name,
                    c.code,
                    COUNT(s.id) AS sales_count,
                    COALESCE(SUM(s."totalAmount"), 0) AS total_sales
                FROM "Cantina" c
                LEFT JOIN "Sale" s ON s."cantinaId" = c.id
                  AND s.status = 'COMPLETED'
                  AND s."createdAt" >= NOW() - (:days || ' days')::interval
                WHERE c."companyId" = :company_id
                GROUP BY c.id, c.name, c.code
                ORDER BY total_sales DESC
                """
            ),
            {"company_id": company_id, "days": days},
        ).fetchall()

        sales_by_product = conn.execute(
            text(
                """
                SELECT 
                    p.id,
                    p.name,
                    p."internalCode",
                    COALESCE(SUM(si.quantity), 0) AS quantity_sold,
                    COALESCE(SUM(si."totalPrice"), 0) AS revenue,
                    COALESCE(SUM(si."grossProfit"), 0) AS gross_profit
                FROM "Product" p
                LEFT JOIN "SaleItem" si ON si."productId" = p.id
                LEFT JOIN "Sale" s ON s.id = si."saleId"
                  AND s.status = 'COMPLETED'
                  AND s."createdAt" >= NOW() - (:days || ' days')::interval
                WHERE p."companyId" = :company_id
                GROUP BY p.id, p.name, p."internalCode"
                ORDER BY revenue DESC
                LIMIT 20
                """
            ),
            {"company_id": company_id, "days": days},
        ).fetchall()

        costs_by_category = conn.execute(
            text(
                """
                SELECT 
                    cc.name AS category,
                    COALESCE(SUM(c.amount), 0) AS total_cost
                FROM "Cost" c
                LEFT JOIN "CostCategory" cc ON cc.id = c."categoryId"
                WHERE c."companyId" = :company_id
                  AND c."paymentStatus" = 'PAID'
                  AND c."costDate" >= NOW() - (:days || ' days')::interval
                GROUP BY cc.name
                ORDER BY total_cost DESC
                """
            ),
            {"company_id": company_id, "days": days},
        ).fetchall()

        stock_risks = conn.execute(
            text(
                """
                SELECT 
                    p.id,
                    p.name,
                    p."internalCode",
                    cs.quantity,
                    p."minStock",
                    p."salePrice"
                FROM "CentralStock" cs
                INNER JOIN "Product" p ON p.id = cs."productId"
                WHERE cs."companyId" = :company_id
                  AND cs.quantity <= p."minStock"
                ORDER BY cs.quantity ASC
                """
            ),
            {"company_id": company_id},
        ).fetchall()

        recent_purchases = conn.execute(
            text(
                """
                SELECT 
                    id,
                    "purchaseNumber",
                    "totalAmount",
                    status,
                    "createdAt"
                FROM "Purchase"
                WHERE "companyId" = :company_id
                ORDER BY "createdAt" DESC
                LIMIT 10
                """
            ),
            {"company_id": company_id},
        ).fetchall()

    return {
        "exists": True,
        "company_id": company_id,
        "company_name": company.name,
        "days": days,
        "sales_by_cantina": [dict(row._mapping) for row in sales_by_cantina],
        "sales_by_product": [dict(row._mapping) for row in sales_by_product],
        "costs_by_category": [dict(row._mapping) for row in costs_by_category],
        "stock_risks": [dict(row._mapping) for row in stock_risks],
        "recent_purchases": [dict(row._mapping) for row in recent_purchases],
    }