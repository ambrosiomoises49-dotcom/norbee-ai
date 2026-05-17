from typing import Any, Dict, List


def build_alert(
    alert_type: str,
    level: str,
    title: str,
    message: str,
    action: str,
    entity_id: str | None = None,
    entity_name: str | None = None,
) -> Dict[str, Any]:
    return {
        "type": alert_type,
        "level": level,
        "title": title,
        "message": message,
        "action": action,
        "entity_id": entity_id,
        "entity_name": entity_name,
    }


def generate_proactive_monitoring(
    feature_store: Dict[str, Any],
    forecast: Dict[str, Any],
    anomalies: Dict[str, Any],
    decisions: List[Dict[str, Any]],
    memory: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    alerts: List[Dict[str, Any]] = []

    stock = feature_store.get("stock", {})
    finance = feature_store.get("finance", {})
    sales = feature_store.get("sales", {})
    cantinas = feature_store.get("cantinas", {})
    forecasting = feature_store.get("forecasting", {})

    stock_health = float(stock.get("stock_health_score") or 0)
    operating_ratio = float(finance.get("operating_ratio") or 0)
    cashflow = float(finance.get("cashflow_estimation") or 0)
    margin = float(sales.get("profit_margin_rate") or 0)
    sales_growth = float(forecasting.get("sales_growth_rate") or 0)
    profit_growth = float(forecasting.get("profit_growth_rate") or 0)

    if stock_health < 70:
        alerts.append(
            build_alert(
                alert_type="stock_health",
                level="high",
                title="Santé du stock faible",
                message=f"Le score stock est de {stock_health:.0f}/100.",
                action="Réapprovisionner les produits critiques en priorité.",
            )
        )

    if operating_ratio > 75:
        alerts.append(
            build_alert(
                alert_type="cost_pressure",
                level="high",
                title="Coûts trop élevés",
                message=f"Les coûts représentent {operating_ratio:.2f}% des ventes.",
                action="Auditer les coûts principaux et réduire les dépenses non essentielles.",
            )
        )

    if cashflow < 0:
        alerts.append(
            build_alert(
                alert_type="cashflow_negative",
                level="high",
                title="Cashflow négatif",
                message=f"Le cashflow estimé est de {cashflow:.2f}.",
                action="Limiter les achats non urgents et augmenter les ventes rapides.",
            )
        )

    if margin < 15:
        alerts.append(
            build_alert(
                alert_type="low_margin",
                level="medium",
                title="Marge faible",
                message=f"La marge estimée est de {margin:.2f}%.",
                action="Revoir les prix et les coûts d’achat des produits à faible marge.",
            )
        )

    if sales_growth < -20:
        alerts.append(
            build_alert(
                alert_type="sales_decline",
                level="high",
                title="Baisse forte des ventes",
                message=f"Les ventes baissent de {sales_growth:.2f}%.",
                action="Identifier les produits et cantinas responsables de la baisse.",
            )
        )

    if profit_growth < -20:
        alerts.append(
            build_alert(
                alert_type="profit_decline",
                level="high",
                title="Baisse forte du bénéfice",
                message=f"Le bénéfice baisse de {profit_growth:.2f}%.",
                action="Analyser les marges, coûts et ruptures de stock.",
            )
        )

    for product in stock.get("critical_products", [])[:5]:
        alerts.append(
            build_alert(
                alert_type="critical_product",
                level="high",
                title=f"Produit critique : {product.get('product')}",
                message=(
                    f"Stock actuel {product.get('quantity')}, "
                    f"minimum {product.get('min_stock')}."
                ),
                action="Acheter ou transférer du stock immédiatement.",
                entity_name=product.get("product"),
            )
        )

    for cantina in cantinas.get("weak_cantinas", [])[:5]:
        alerts.append(
            build_alert(
                alert_type="weak_cantina",
                level="medium",
                title=f"Cantina faible : {cantina.get('name')}",
                message="Cette cantina vend très en dessous de la moyenne.",
                action="Auditer stock, équipe, emplacement et saisie des ventes.",
                entity_id=cantina.get("id"),
                entity_name=cantina.get("name"),
            )
        )

    for anomaly in anomalies.get("advanced", {}).get("anomalies", [])[:8]:
        alerts.append(
            build_alert(
                alert_type=anomaly.get("type", "advanced_anomaly"),
                level=anomaly.get("level", "medium"),
                title=anomaly.get("title", "Anomalie détectée"),
                message=anomaly.get("message", ""),
                action=anomaly.get("recommendation", "Analyser cette anomalie."),
                entity_id=anomaly.get("entity_id"),
                entity_name=anomaly.get("entity_name"),
            )
        )

    if memory and memory.get("risk_evolution") == "increased":
        alerts.append(
            build_alert(
                alert_type="risk_increase",
                level="high",
                title="Risque en augmentation",
                message=memory.get("message", "Le risque augmente depuis la dernière analyse."),
                action="Traiter immédiatement les décisions prioritaires.",
            )
        )

    high_decisions = [
        decision for decision in decisions
        if decision.get("priority") == "high"
    ]

    for decision in high_decisions[:5]:
        alerts.append(
            build_alert(
                alert_type=f"decision_{decision.get('type', 'action')}",
                level="high",
                title=decision.get("title", "Décision prioritaire"),
                message=decision.get("reason", ""),
                action=decision.get("action", ""),
                entity_id=decision.get("entity_id"),
                entity_name=decision.get("entity_name"),
            )
        )

    unique_alerts = []
    seen = set()

    for alert in alerts:
        key = f"{alert.get('type')}::{alert.get('title')}::{alert.get('entity_name')}"
        if key not in seen:
            seen.add(key)
            unique_alerts.append(alert)

    high_count = len([a for a in unique_alerts if a.get("level") == "high"])
    medium_count = len([a for a in unique_alerts if a.get("level") == "medium"])

    return {
        "engine": "proactive_monitoring_v2",
        "status": "ok",
        "total_alerts": len(unique_alerts),
        "high_count": high_count,
        "medium_count": medium_count,
        "alerts": unique_alerts,
    }