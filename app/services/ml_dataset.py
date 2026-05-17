from sqlalchemy import text

from app.database.database import engine


def build_ml_dataset(company_id: str, days: int = 30):
    with engine.connect() as conn:
        company = conn.execute(
            text(
                """
                SELECT id
                FROM "Company"
                WHERE id = :company_id
                LIMIT 1
                """
            ),
            {"company_id": company_id},
        ).fetchone()

        if not company:
            return {
                "company_id": company_id,
                "exists": False,
                "sales_history": [],
                "profit_history": [],
                "stock_history": [],
                "days": days,
            }

        sales_rows = conn.execute(
            text(
                """
                SELECT 
                    DATE("createdAt") AS day,
                    SUM("totalAmount") AS total_sales
                FROM "Sale"
                WHERE "companyId" = :company_id
                  AND status = 'COMPLETED'
                  AND "createdAt" >= NOW() - (:days || ' days')::interval
                GROUP BY DATE("createdAt")
                ORDER BY day ASC
                """
            ),
            {
                "company_id": company_id,
                "days": days,
            },
        ).fetchall()

        cost_rows = conn.execute(
            text(
                """
                SELECT 
                    DATE("costDate") AS day,
                    SUM(amount) AS total_costs
                FROM "Cost"
                WHERE "companyId" = :company_id
                  AND "paymentStatus" = 'PAID'
                  AND "costDate" >= NOW() - (:days || ' days')::interval
                GROUP BY DATE("costDate")
                ORDER BY day ASC
                """
            ),
            {
                "company_id": company_id,
                "days": days,
            },
        ).fetchall()

        stock_rows = conn.execute(
            text(
                """
                SELECT 
                    SUM(quantity) AS total_stock
                FROM "CentralStock"
                WHERE "companyId" = :company_id
                """
            ),
            {
                "company_id": company_id,
            },
        ).fetchall()

    sales_by_day = {
        str(row.day): float(row.total_sales or 0)
        for row in sales_rows
    }

    costs_by_day = {
        str(row.day): float(row.total_costs or 0)
        for row in cost_rows
    }

    all_days = sorted(set(sales_by_day.keys()) | set(costs_by_day.keys()))

    sales_history = []
    profit_history = []

    for day in all_days:
        sales = sales_by_day.get(day, 0)
        costs = costs_by_day.get(day, 0)

        sales_history.append(sales)
        profit_history.append(sales - costs)

    total_stock = 0

    if stock_rows and stock_rows[0].total_stock is not None:
        total_stock = float(stock_rows[0].total_stock or 0)

    return {
        "company_id": company_id,
        "exists": True,
        "sales_history": sales_history,
        "profit_history": profit_history,
        "stock_history": [total_stock],
        "days": days,
    }