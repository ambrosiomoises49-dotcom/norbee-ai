from typing import Any, Dict, List


def money(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def classify_question(question: str) -> Dict[str, Any]:
    q = question.lower()

    intents = []

    if any(w in q for w in ["bénéfice", "benefice", "lucro", "profit", "marge", "margin"]):
        intents.append("profit")

    if any(w in q for w in ["vente", "vendas", "sales", "chiffre", "faturamento"]):
        intents.append("sales")

    if any(w in q for w in ["stock", "rupture", "acheter", "comprar", "repor", "produit", "produto"]):
        intents.append("stock")

    if any(w in q for w in ["coût", "cout", "custo", "despesa", "expense", "charge"]):
        intents.append("costs")

    if any(w in q for w in ["cantina", "loja", "store", "point de vente"]):
        intents.append("cantina")

    if any(w in q for w in ["risque", "risco", "alerta", "alerte", "danger"]):
        intents.append("risk")

    if any(w in q for w in ["prévoir", "prevoir", "previsão", "forecast", "futur", "prochain"]):
        intents.append("forecast")

    if not intents:
        intents.append("general")

    return {
        "intents": intents,
        "main_intent": intents[0],
    }


def analyze_profit_causes(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    causes = []

    sales_by_product = dataset.get("sales_by_product", [])
    costs_by_category = dataset.get("costs_by_category", [])
    sales_by_cantina = dataset.get("sales_by_cantina", [])
    stock_risks = dataset.get("stock_risks", [])

    total_sales = sum(money(c.get("total_sales")) for c in sales_by_cantina)
    total_costs = sum(money(c.get("total_cost")) for c in costs_by_category)
    total_profit = sum(money(p.get("gross_profit")) for p in sales_by_product)

    if total_sales > 0 and total_costs > total_sales * 0.65:
        top_cost = costs_by_category[0] if costs_by_category else None

        causes.append({
            "level": "high",
            "type": "cost_pressure",
            "title": "Coûts trop élevés par rapport aux ventes",
            "explanation": (
                f"Les coûts représentent environ {(total_costs / total_sales) * 100:.1f}% "
                f"des ventes du période analysée."
            ),
            "evidence": top_cost,
            "action": "Réduire les coûts dominants, négocier fournisseurs et contrôler dépenses fixes.",
        })

    negative_margin_products = [
        p for p in sales_by_product
        if money(p.get("revenue")) > 0 and money(p.get("gross_profit")) < 0
    ]

    for product in negative_margin_products[:3]:
        causes.append({
            "level": "high",
            "type": "negative_margin",
            "title": f"Marge négative sur {product.get('name')}",
            "explanation": (
                f"Le produit {product.get('name')} a généré du chiffre d’affaires "
                f"mais un profit brut négatif."
            ),
            "evidence": product,
            "action": "Revoir prix de vente, coût FIFO, remises et erreurs de saisie.",
        })

    if total_profit < total_sales * 0.15 and total_sales > 0:
        causes.append({
            "level": "medium",
            "type": "weak_margin",
            "title": "Marge globale faible",
            "explanation": (
                f"Le profit brut estimé est faible par rapport aux ventes. "
                f"Profit brut: {total_profit:.2f}, ventes: {total_sales:.2f}."
            ),
            "evidence": {
                "total_sales": total_sales,
                "total_profit": total_profit,
            },
            "action": "Identifier produits à faible marge et ajuster prix ou achats.",
        })

    if stock_risks:
        causes.append({
            "level": "medium",
            "type": "stockout_impact",
            "title": "Ruptures de stock pouvant réduire les ventes",
            "explanation": (
                f"{len(stock_risks)} produit(s) sont sous le stock minimum ou en rupture."
            ),
            "evidence": stock_risks[:3],
            "action": "Réapprovisionner les produits critiques pour éviter perte de chiffre d’affaires.",
        })

    weak_cantinas = [
        c for c in sales_by_cantina
        if money(c.get("total_sales")) == 0
    ]

    if weak_cantinas:
        causes.append({
            "level": "medium",
            "type": "inactive_cantina",
            "title": "Cantinas sans ventes",
            "explanation": (
                f"{len(weak_cantinas)} cantina(s) n’ont généré aucune vente sur la période."
            ),
            "evidence": weak_cantinas[:3],
            "action": "Vérifier activité, stock disponible, équipe et configuration de ces cantinas.",
        })

    return causes


def analyze_stock_actions(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions = []

    for product in dataset.get("stock_risks", [])[:5]:
        quantity = money(product.get("quantity"))
        min_stock = money(product.get("minStock"))
        sale_price = money(product.get("salePrice"))

        recommended_qty = max((min_stock * 2) - quantity, min_stock, 1)

        actions.append({
            "level": "high" if quantity <= 0 else "medium",
            "type": "purchase",
            "title": f"Réapprovisionner {product.get('name')}",
            "explanation": (
                f"Stock actuel: {quantity:.0f}. Stock minimum: {min_stock:.0f}."
            ),
            "action": f"Acheter ou transférer environ {recommended_qty:.0f} unités.",
            "estimated_revenue_protected": round(recommended_qty * sale_price, 2),
            "evidence": product,
        })

    return actions


def analyze_cantina_performance(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    insights = []

    cantinas = dataset.get("sales_by_cantina", [])
    active = [c for c in cantinas if money(c.get("total_sales")) > 0]

    if not cantinas:
        return insights

    best = cantinas[0]

    if money(best.get("total_sales")) > 0:
        insights.append({
            "level": "low",
            "type": "best_cantina",
            "title": f"Meilleure cantina: {best.get('name')}",
            "explanation": (
                f"{best.get('name')} domine avec {money(best.get('total_sales')):.2f} de ventes."
            ),
            "action": "Analyser ses produits, horaires, équipe et méthode pour reproduire ailleurs.",
            "evidence": best,
        })

    if len(active) >= 2:
        avg = sum(money(c.get("total_sales")) for c in active) / len(active)

        for cantina in active:
            if money(cantina.get("total_sales")) < avg * 0.4:
                insights.append({
                    "level": "medium",
                    "type": "weak_cantina",
                    "title": f"Cantina faible: {cantina.get('name')}",
                    "explanation": (
                        f"Ses ventes sont très inférieures à la moyenne des cantinas actives."
                    ),
                    "action": "Vérifier stock, personnel, emplacement, clientèle et saisie des ventes.",
                    "evidence": cantina,
                })

    return insights


def build_natural_answer(
    question: str,
    classification: Dict[str, Any],
    dataset: Dict[str, Any],
) -> Dict[str, Any]:
    intents = classification["intents"]

    profit_causes = analyze_profit_causes(dataset)
    stock_actions = analyze_stock_actions(dataset)
    cantina_insights = analyze_cantina_performance(dataset)

    reasoning_steps = []
    decisions = []

    if "profit" in intents:
        reasoning_steps.extend(profit_causes)

    if "stock" in intents:
        reasoning_steps.extend(stock_actions)

    if "cantina" in intents or "sales" in intents:
        reasoning_steps.extend(cantina_insights)

    if "general" in intents or not reasoning_steps:
        reasoning_steps.extend(profit_causes[:2])
        reasoning_steps.extend(stock_actions[:2])
        reasoning_steps.extend(cantina_insights[:2])

    for step in reasoning_steps:
        decisions.append({
            "priority": step["level"],
            "type": step["type"],
            "title": step["title"],
            "reason": step["explanation"],
            "action": step["action"],
        })

    if not reasoning_steps:
        answer = (
            "Je n’ai pas trouvé assez de signaux forts dans les données actuelles. "
            "Je peux analyser les ventes, les marges, les coûts, le stock ou les cantinas."
        )
    else:
        main = reasoning_steps[0]

        answer_lines = [
            f"Mon analyse principale : {main['title']}.",
            "",
            "Les causes ou signaux les plus importants sont :",
        ]

        for index, step in enumerate(reasoning_steps[:5], start=1):
            answer_lines.append(
                f"{index}. {step['title']} — {step['explanation']}"
            )

        answer_lines.append("")
        answer_lines.append("Je recommande :")

        for index, step in enumerate(reasoning_steps[:5], start=1):
            answer_lines.append(
                f"{index}. {step['action']}"
            )

        answer = "\n".join(answer_lines)

    return {
        "answer": answer,
        "intents": intents,
        "reasoning_steps": reasoning_steps,
        "decisions": decisions,
    }