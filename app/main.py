from fastapi import FastAPI
from app.routes.finance_agent import router as finance_agent_router
from app.routes.sales_agent import router as sales_agent_router
from app.routes.stock_agent import router as stock_agent_router
from app.routes.health import router as health_router
from app.routes.ai_analysis import router as ai_analysis_router
from app.routes.stock_forecast import router as stock_forecast_router
from app.routes.orchestrator import router as orchestrator_router
from app.routes.memory import router as memory_router
from app.routes.proactive import router as proactive_router
from app.routes.alerts import router as alerts_router
from app.routes.ml_analysis import router as ml_analysis_router
from app.routes.company_ml import router as company_ml_router
from app.routes.chat import router as chat_router
from app.routes.proactive_monitoring import router as proactive_monitoring_router




app = FastAPI(
    title="Norbee AI",
    description="Moteur d'intelligence artificielle avancée pour Norbee ERP",
    version="1.0.0",
)

app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(ai_analysis_router, prefix="/ai", tags=["AI Analysis"])
app.include_router(stock_forecast_router, prefix="/ai/stock-forecast", tags=["Stock Forecast"])
app.include_router(stock_agent_router, prefix="/agents/stock", tags=["Agents"])
app.include_router(sales_agent_router, prefix="/agents/sales", tags=["Agents"])
app.include_router(finance_agent_router, prefix="/agents/finance", tags=["Agents"])
app.include_router(orchestrator_router, prefix="/agents/orchestrator", tags=["Orchestrator"])
app.include_router(memory_router, prefix="/memory", tags=["Memory"])
app.include_router(proactive_router, prefix="/proactive", tags=["Proactive AI"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(ml_analysis_router, prefix="/api/ai", tags=["ML Analysis"])
app.include_router(
    company_ml_router,
    prefix="/api/ai",
    tags=["Company ML Analysis"],
)
app.include_router(chat_router, prefix="/api/ai", tags=["AI Chat"])
app.include_router(
    proactive_monitoring_router,
    prefix="/api/ai",
    tags=["Proactive Monitoring"],
)