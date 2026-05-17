AI_TEXTS = {
    "critical_stockout_title": {
        "pt": "Ruptura crítica",
        "fr": "Rupture critique",
        "en": "Critical stockout",
    },
    "probable_stockout_title": {
        "pt": "Ruptura provável",
        "fr": "Rupture probable",
        "en": "Probable stockout",
    },
    "stock_to_watch_title": {
        "pt": "Stock a vigiar",
        "fr": "Stock à surveiller",
        "en": "Stock to monitor",
    },
    "critical_stockout_message": {
        "pt": "{product} está em situação crítica. Stock atual: {stock}. Stock mínimo: {min_stock}.",
        "fr": "{product} est en situation critique. Stock actuel : {stock}. Stock minimum : {min_stock}.",
        "en": "{product} is in a critical situation. Current stock: {stock}. Minimum stock: {min_stock}.",
    },
    "probable_stockout_message": {
        "pt": "{product} pode ficar em ruptura dentro de aproximadamente {days} dias.",
        "fr": "{product} pourrait être en rupture dans environ {days} jours.",
        "en": "{product} could be out of stock in about {days} days.",
    },
    "stock_to_watch_message": {
        "pt": "{product} deve ser acompanhado. Ruptura estimada em {days} dias.",
        "fr": "{product} doit être surveillé. Rupture estimée dans {days} jours.",
        "en": "{product} should be monitored. Estimated stockout in {days} days.",
    },
    "order_critical_products": {
        "pt": "Encomendar imediatamente os produtos em ruptura crítica.",
        "fr": "Commander immédiatement les produits en rupture critique.",
        "en": "Order critical stockout products immediately.",
    },
    "plan_fast_restock": {
        "pt": "Planear rapidamente o reabastecimento dos produtos de alta rotação.",
        "fr": "Planifier rapidement le réapprovisionnement des produits à forte rotation.",
        "en": "Quickly plan restocking for high-turnover products.",
    },
    "stock_stable": {
        "pt": "O stock parece estável. Continuar a vigilância regular.",
        "fr": "Le stock semble stable. Continuer la surveillance régulière.",
        "en": "Stock seems stable. Continue regular monitoring.",
    },
    "analysis_summary": {
        "pt": "Análise IA realizada em {count} produto(s). {alerts} alerta(s) detectado(s), incluindo {critical} crítico(s).",
        "fr": "Analyse IA effectuée sur {count} produit(s). {alerts} alerte(s) détectée(s), dont {critical} critique(s).",
        "en": "AI analysis performed on {count} product(s). {alerts} alert(s) detected, including {critical} critical.",
    },
}


def t(key: str, lang: str = "pt", **kwargs):
    safe_lang = lang if lang in ["pt", "fr", "en"] else "pt"
    text = AI_TEXTS.get(key, {}).get(safe_lang, key)

    if kwargs:
        return text.format(**kwargs)

    return text