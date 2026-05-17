from fastapi import APIRouter

from app.schemas.orchestrator import OrchestratorInput
from app.agents.orchestrator import run_orchestrator

router = APIRouter()


@router.post("/")
def orchestrator(payload: OrchestratorInput):
    return run_orchestrator(payload)