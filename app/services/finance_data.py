import pandas as pd
from app.database.db import engine


def load_monthly_finance(company_id: str):
    income_query = """
        SELECT
            DATE_TRUNC('month', "date") AS month,
            SUM(amount) AS total
        FROM "FinanceTransaction"
        WHERE "companyId" = %(company_id)s
          AND type = 'INCOME'
        GROUP BY DATE_TRUNC('month', "date")
        ORDER BY month ASC
    """

    expense_query = """
        SELECT
            DATE_TRUNC('month', "date") AS month,
            SUM(amount) AS total
        FROM "FinanceTransaction"
        WHERE "companyId" = %(company_id)s
          AND type = 'EXPENSE'
        GROUP BY DATE_TRUNC('month', "date")
        ORDER BY month ASC
    """

    accounts_query = """
        SELECT SUM(balance) AS balance
        FROM "FinancialAccount"
        WHERE "companyId" = %(company_id)s
    """

    costs_query = """
        SELECT description, amount, "costDate"
        FROM "Cost"
        WHERE "companyId" = %(company_id)s
        ORDER BY "costDate" DESC
        LIMIT 20
    """

    income_df = pd.read_sql(income_query, engine, params={"company_id": company_id})
    expense_df = pd.read_sql(expense_query, engine, params={"company_id": company_id})
    accounts_df = pd.read_sql(accounts_query, engine, params={"company_id": company_id})
    costs_df = pd.read_sql(costs_query, engine, params={"company_id": company_id})

    return {
        "monthly_income": income_df["total"].astype(float).tolist() if not income_df.empty else [],
        "monthly_expenses": expense_df["total"].astype(float).tolist() if not expense_df.empty else [],
        "cash_balance": float(accounts_df.iloc[0]["balance"] or 0) if not accounts_df.empty else 0,
        "recent_costs": costs_df.to_dict(orient="records") if not costs_df.empty else [],
    }