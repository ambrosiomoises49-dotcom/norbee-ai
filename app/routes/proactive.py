from fastapi import APIRouter

from app.schemas.orchestrator import OrchestratorInput
from app.agents.orchestrator import run_orchestrator
from app.proactive.proactive_engine import generate_proactive_alerts

router = APIRouter()


@router.post("/")
def proactive_analysis(payload: OrchestratorInput):
    orchestrator_result = run_orchestrator(payload)

    alerts = generate_proactive_alerts(orchestrator_result)

    return {
        "status": "success",
        "alerts_count": len(alerts),
        "alerts": alerts,
        "orchestrator": orchestrator_result,
    }
