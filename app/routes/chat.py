from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.services.rich_dataset import build_rich_company_dataset
from fastapi import APIRouter, Depends
from app.core.security import verify_api_key

router = APIRouter()

@router.post("/chat", dependencies=[Depends(verify_api_key)])

class ChatInput(BaseModel):
    company_id: str
    question: str
    lang: str = "pt"
    days: int = 30


def detect_intent(question: str):
    q = question.lower()

    if any(word in q for word in ["stock", "estoque", "ruptura", "produto"]):
        return "stock"

    if any(word in q for word in ["venda", "ventes", "sales", "cantina"]):
        return "sales"

    if any(word in q for word in ["lucro", "profit", "benefício", "margem"]):
        return "profit"

    if any(word in q for word in ["custo", "despesa", "cost", "expense"]):
        return "costs"

    if any(word in q for word in ["risco", "risk", "alerte", "alerta"]):
        return "risk"

    return "general"


def build_answer(question: str, dataset: dict, lang: str = "pt"):
    intent = detect_intent(question)

    if not dataset.get("exists"):
        return {
            "answer": "Empresa não encontrada.",
            "intent": intent,
            "recommendations": [],
        }

    recommendations = []

    stock_risks = dataset.get("stock_risks", [])
    sales_by_product = dataset.get("sales_by_product", [])
    sales_by_cantina = dataset.get("sales_by_cantina", [])
    costs_by_category = dataset.get("costs_by_category", [])

    if intent == "stock":
        if stock_risks:
            product = stock_risks[0]
            answer = (
                f"O principal risco de stock é {product['name']}. "
                f"Quantidade atual: {product['quantity']}, stock mínimo: {product['minStock']}."
            )
            recommendations.append(
                f"Comprar ou repor rapidamente o produto {product['name']}."
            )
        else:
            answer = "Não encontrei ruptura crítica de stock neste momento."

    elif intent == "sales":
        if sales_by_cantina:
            best = sales_by_cantina[0]
            answer = (
                f"A cantina com melhor desempenho é {best['name']} "
                f"com total de vendas de {float(best['total_sales']):.2f}."
            )
            recommendations.append(
                "Comparar a estratégia da melhor cantina com as outras cantinas."
            )
        else:
            answer = "Não encontrei vendas suficientes no período analisado."

    elif intent == "profit":
        if sales_by_product:
            best = sales_by_product[0]
            answer = (
                f"O produto com maior contribuição recente é {best['name']} "
                f"com lucro bruto de {float(best['gross_profit']):.2f}."
            )
            recommendations.append(
                f"Manter disponibilidade do produto {best['name']} e analisar margem."
            )
        else:
            answer = "Ainda não há dados suficientes para analisar lucro por produto."

    elif intent == "costs":
        if costs_by_category:
            cost = costs_by_category[0]
            answer = (
                f"A maior categoria de custo é {cost['category']} "
                f"com total de {float(cost['total_cost']):.2f}."
            )
            recommendations.append(
                f"Rever a categoria de custo {cost['category']} para reduzir despesas."
            )
        else:
            answer = "Não encontrei custos pagos relevantes no período analisado."

    elif intent == "risk":
        if stock_risks:
            answer = (
                f"Detectei {len(stock_risks)} risco(s) de stock. "
                "A prioridade é evitar rupturas nos produtos abaixo do mínimo."
            )
            recommendations.append("Priorizar reposição dos produtos em ruptura.")
        else:
            answer = "Não detectei risco crítico imediato."

    else:
        answer = (
            "Analisei vendas, stock, custos, compras e cantinas. "
            "Podes perguntar sobre stock, vendas, lucro, custos ou riscos."
        )

    return {
        "answer": answer,
        "intent": intent,
        "recommendations": recommendations,
    }


@router.post("/chat", dependencies=[Depends(verify_api_key)])
async def ai_chat(payload: ChatInput):
    dataset = build_rich_company_dataset(
        company_id=payload.company_id,
        days=payload.days,
    )

    result = build_answer(
        question=payload.question,
        dataset=dataset,
        lang=payload.lang,
    )

    return {
        "agent": "chat",
        "status": "ok" if dataset.get("exists") else "not_found",
        "company_id": payload.company_id,
        "question": payload.question,
        "intent": result["intent"],
        "answer": result["answer"],
        "recommendations": result["recommendations"],
        "context": {
            "days": payload.days,
            "stock_risks_count": len(dataset.get("stock_risks", [])),
            "products_analyzed": len(dataset.get("sales_by_product", [])),
            "cantinas_analyzed": len(dataset.get("sales_by_cantina", [])),
        },
    }