from collections import defaultdict
from typing import Any, Dict, List

from app.schemas.finance import FinanceTransactionInput


def analyze_finance_agent(
    transactions: list[FinanceTransactionInput],
    lang: str = "pt",
) -> Dict[str, Any]:

    income = 0.0
    expense = 0.0

    expenses_by_category = defaultdict(float)

    for tx in transactions:
        amount = float(tx.amount or 0)

        if tx.type == "INCOME":
            income += amount

        if tx.type == "EXPENSE":
            expense += amount

            category = (
                tx.category
                or tx.reference_type
                or "Outros"
            )

            expenses_by_category[category] += amount

    balance = income - expense

    top_expenses = sorted(
        [
            {
                "category": category,
                "amount": round(amount, 2),
            }
            for category, amount in expenses_by_category.items()
        ],
        key=lambda item: float(item["amount"]),
        reverse=True,
    )

    recommendations: List[str] = []

    if expense > income:
        recommendations.append(
            "As despesas estão superiores às entradas. Rever custos fixos e despesas operacionais."
        )

    if balance > 0:
        recommendations.append(
            "O saldo financeiro é positivo. Manter acompanhamento do fluxo de caixa."
        )

    if balance < 0:
        recommendations.append(
            "O saldo financeiro é negativo. Reduzir despesas e reforçar receitas."
        )

    if top_expenses:
        recommendations.append(
            f"A maior fonte de despesa é {top_expenses[0]['category']}."
        )

    return {
        "agent": "finance_agent",
        "status": "ok",
        "total_transactions": len(transactions),
        "income": round(income, 2),
        "expense": round(expense, 2),
        "balance": round(balance, 2),
        "top_expenses": top_expenses,
        "recommendations": recommendations,
    }


def analyze_finance(
    transactions: list[FinanceTransactionInput],
    lang: str = "pt",
) -> Dict[str, Any]:
    """
    Alias compatible avec app/routes/alerts.py
    """
    return analyze_finance_agent(
        transactions=transactions,
        lang=lang,
    )