from typing import Any, Dict, List


def build_decision(
    decision_type: str,
    priority: str,
    title: str,
    reason: str,
    action: str,
    entity_id: str | None = None,
    entity_name: str | None = None,
    estimated_impact: float | None = None,
) -> Dict[str, Any]:
    return {
        "type": decision_type,
        "priority": priority,
        "title": title,
        "reason": reason,
        "action": action,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "estimated_impact": estimated_impact,
    }


def generate_advanced_decisions(
    rich_dataset: Dict[str, Any],
    forecast: Dict[str, Any],
    trend_analysis: Dict[str, Any],
    anomalies: Dict[str, Any],
    risk_score: Dict[str, Any],
) -> List[Dict[str, Any]]:
    decisions: List[Dict[str, Any]] = []

    stock_risks = rich_dataset.get("stock_risks", [])
    sales_by_product = rich_dataset.get("sales_by_product", [])
    sales_by_cantina = rich_dataset.get("sales_by_cantina", [])
    costs_by_category = rich_dataset.get("costs_by_category", [])
    advanced_anomalies = anomalies.get("advanced", {}).get("anomalies", [])

    # 1. Comprar produto em ruptura ou abaixo do mínimo
    for product in stock_risks[:5]:
        quantity = float(product.get("quantity") or 0)
        min_stock = float(product.get("minStock") or 0)
        sale_price = float(product.get("salePrice") or 0)

        recommended_qty = max((min_stock * 2) - quantity, min_stock, 1)
        estimated_impact = recommended_qty * sale_price

        decisions.append(
            build_decision(
                decision_type="purchase",
                priority="high" if quantity <= 0 else "medium",
                title=f"Comprar {product.get('name')}",
                reason=(
                    f"O produto está com stock {quantity} e mínimo definido em {min_stock}."
                ),
                action=(
                    f"Comprar ou repor aproximadamente {recommended_qty:.0f} unidades."
                ),
                entity_id=product.get("id"),
                entity_name=product.get("name"),
                estimated_impact=round(estimated_impact, 2),
            )
        )

    # 2. Rever margem negativa
    for anomaly in advanced_anomalies:
        if anomaly.get("type") == "negative_margin":
            decisions.append(
                build_decision(
                    decision_type="price_review",
                    priority="high",
                    title=f"Rever preço/margem de {anomaly.get('entity_name')}",
                    reason=anomaly.get("message", ""),
                    action=(
                        "Verificar custo FIFO, preço de venda, descontos e atualizar margem mínima."
                    ),
                    entity_id=anomaly.get("entity_id"),
                    entity_name=anomaly.get("entity_name"),
                    estimated_impact=abs(float(anomaly.get("value") or 0)),
                )
            )

    # 3. Investigar cantina suspeita
    for anomaly in advanced_anomalies:
        if anomaly.get("type") == "suspicious_cantina":
            decisions.append(
                build_decision(
                    decision_type="investigate_cantina",
                    priority="medium",
                    title=f"Investigar cantina {anomaly.get('entity_name')}",
                    reason=anomaly.get("message", ""),
                    action=(
                        "Verificar stock disponível, equipa, fluxo de clientes e registo correto das vendas."
                    ),
                    entity_id=anomaly.get("entity_id"),
                    entity_name=anomaly.get("entity_name"),
                    estimated_impact=None,
                )
            )

    # 4. Reduzir custo dominante
    if costs_by_category:
        top_cost = costs_by_category[0]
        total_cost = float(top_cost.get("total_cost") or 0)

        if total_cost > 0:
            decisions.append(
                build_decision(
                    decision_type="reduce_cost",
                    priority="medium",
                    title=f"Reduzir custo: {top_cost.get('category')}",
                    reason=(
                        f"A categoria {top_cost.get('category')} é a maior fonte de custo no período."
                    ),
                    action=(
                        "Auditar esta categoria, negociar fornecedores e eliminar despesas não essenciais."
                    ),
                    entity_id=None,
                    entity_name=top_cost.get("category"),
                    estimated_impact=round(total_cost * 0.1, 2),
                )
            )

    # 5. Reforçar produto mais vendido
    if sales_by_product:
        top_product = sales_by_product[0]
        revenue = float(top_product.get("revenue") or 0)

        if revenue > 0:
            decisions.append(
                build_decision(
                    decision_type="boost_product",
                    priority="medium",
                    title=f"Reforçar produto campeão: {top_product.get('name')}",
                    reason=(
                        f"O produto gerou {revenue:.2f} de receita no período analisado."
                    ),
                    action=(
                        "Garantir stock contínuo, melhorar exposição e avaliar aumento controlado de preço."
                    ),
                    entity_id=top_product.get("id"),
                    entity_name=top_product.get("name"),
                    estimated_impact=round(revenue * 0.05, 2),
                )
            )

    # 6. Replicar melhor cantina
    if sales_by_cantina:
        best_cantina = sales_by_cantina[0]
        total_sales = float(best_cantina.get("total_sales") or 0)

        if total_sales > 0:
            decisions.append(
                build_decision(
                    decision_type="replicate_best_cantina",
                    priority="low",
                    title=f"Replicar estratégia da cantina {best_cantina.get('name')}",
                    reason=(
                        f"Esta cantina lidera as vendas com {total_sales:.2f} no período."
                    ),
                    action=(
                        "Comparar horários, equipa, produtos vendidos e organização com as outras cantinas."
                    ),
                    entity_id=best_cantina.get("id"),
                    entity_name=best_cantina.get("name"),
                    estimated_impact=None,
                )
            )

    # 7. Se risco global alto, ação executiva
    if risk_score.get("level") == "high":
        decisions.insert(
            0,
            build_decision(
                decision_type="executive_review",
                priority="high",
                title="Revisão executiva urgente",
                reason="O score global de risco está elevado.",
                action=(
                    "Reunir vendas, stock e finanças para decidir compras, cortes de custos e ações comerciais."
                ),
                entity_id=None,
                entity_name="Entreprise",
                estimated_impact=None,
            ),
        )

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    decisions = sorted(
        decisions,
        key=lambda item: priority_order.get(item["priority"], 3),
    )

    return decisions[:12]