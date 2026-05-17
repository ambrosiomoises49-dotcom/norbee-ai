from typing import Any, Dict, List


def detect_advanced_anomalies(dataset: Dict[str, Any]) -> Dict[str, Any]:
    anomalies: List[Dict[str, Any]] = []

    sales_by_cantina = dataset.get("sales_by_cantina", [])
    sales_by_product = dataset.get("sales_by_product", [])
    costs_by_category = dataset.get("costs_by_category", [])
    stock_risks = dataset.get("stock_risks", [])

    total_sales = sum(float(c.get("total_sales") or 0) for c in sales_by_cantina)
    total_costs = sum(float(c.get("total_cost") or 0) for c in costs_by_category)

    # 1. Cantina suspeita: vendas muito baixas face às outras
    active_cantinas = [
        c for c in sales_by_cantina if float(c.get("total_sales") or 0) > 0
    ]

    if len(active_cantinas) >= 3:
        avg_sales = sum(float(c.get("total_sales") or 0) for c in active_cantinas) / len(active_cantinas)

        for cantina in active_cantinas:
            total = float(cantina.get("total_sales") or 0)

            if total < avg_sales * 0.35:
                anomalies.append({
                    "type": "suspicious_cantina",
                    "level": "medium",
                    "title": f"Cantina com desempenho anormal: {cantina.get('name')}",
                    "message": (
                        f"A cantina {cantina.get('name')} apresenta vendas muito abaixo da média."
                    ),
                    "entity_id": cantina.get("id"),
                    "entity_name": cantina.get("name"),
                    "value": round(total, 2),
                    "reference": round(avg_sales, 2),
                    "recommendation": (
                        "Investigar fluxo de clientes, stock disponível, equipa, localização e registo de vendas."
                    ),
                })

    # 2. Margem negativa por produto
    for product in sales_by_product:
        revenue = float(product.get("revenue") or 0)
        gross_profit = float(product.get("gross_profit") or 0)

        if revenue > 0 and gross_profit < 0:
            anomalies.append({
                "type": "negative_margin",
                "level": "high",
                "title": f"Margem negativa: {product.get('name')}",
                "message": (
                    f"O produto {product.get('name')} gerou receita mas apresentou lucro bruto negativo."
                ),
                "entity_id": product.get("id"),
                "entity_name": product.get("name"),
                "value": round(gross_profit, 2),
                "reference": round(revenue, 2),
                "recommendation": (
                    "Rever preço de venda, custo FIFO, descontos e possíveis erros de registo."
                ),
            })

    # 3. Stock incoerente
    for stock in stock_risks:
        quantity = float(stock.get("quantity") or 0)
        min_stock = float(stock.get("minStock") or 0)

        if quantity < 0:
            anomalies.append({
                "type": "inconsistent_stock",
                "level": "high",
                "title": f"Stock negativo: {stock.get('name')}",
                "message": (
                    f"O produto {stock.get('name')} tem quantidade negativa no stock."
                ),
                "entity_id": stock.get("id"),
                "entity_name": stock.get("name"),
                "value": quantity,
                "reference": min_stock,
                "recommendation": (
                    "Corrigir inventário, movimentos de stock e possíveis vendas sem stock suficiente."
                ),
            })

        elif quantity == 0 and min_stock > 0:
            anomalies.append({
                "type": "stockout",
                "level": "high",
                "title": f"Ruptura de stock: {stock.get('name')}",
                "message": (
                    f"O produto {stock.get('name')} está sem stock e possui stock mínimo definido."
                ),
                "entity_id": stock.get("id"),
                "entity_name": stock.get("name"),
                "value": quantity,
                "reference": min_stock,
                "recommendation": (
                    "Comprar ou transferir stock com urgência."
                ),
            })

    # 4. Explosão de custos
    if total_sales > 0 and total_costs > total_sales * 0.75:
        anomalies.append({
            "type": "cost_explosion",
            "level": "high",
            "title": "Custos elevados face às vendas",
            "message": (
                "Os custos pagos representam mais de 75% das vendas do período."
            ),
            "entity_id": None,
            "entity_name": "Finance",
            "value": round(total_costs, 2),
            "reference": round(total_sales, 2),
            "recommendation": (
                "Rever categorias de custo, despesas fixas e despesas extraordinárias."
            ),
        })

    # 5. Queda brusca de vendas por produto
    if sales_by_product:
        products_with_sales = [
            p for p in sales_by_product if float(p.get("revenue") or 0) > 0
        ]

        if len(products_with_sales) >= 5:
            avg_revenue = sum(float(p.get("revenue") or 0) for p in products_with_sales) / len(products_with_sales)

            for product in products_with_sales:
                revenue = float(product.get("revenue") or 0)

                if revenue < avg_revenue * 0.2:
                    anomalies.append({
                        "type": "low_product_sales",
                        "level": "medium",
                        "title": f"Produto com vendas muito fracas: {product.get('name')}",
                        "message": (
                            f"O produto {product.get('name')} vendeu muito abaixo da média dos produtos vendidos."
                        ),
                        "entity_id": product.get("id"),
                        "entity_name": product.get("name"),
                        "value": round(revenue, 2),
                        "reference": round(avg_revenue, 2),
                        "recommendation": (
                            "Verificar preço, exposição, disponibilidade e procura real do produto."
                        ),
                    })

    return {
        "status": "ok",
        "count": len(anomalies),
        "anomalies": anomalies,
    }