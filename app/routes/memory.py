from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_memory import (
    save_memory,
    get_memory,
    get_recent_memory,
    summarize_memory,
)

router = APIRouter()


class MemoryInput(BaseModel):
    company_id: str
    category: str
    data: dict


@router.post("/")
def create_memory(payload: MemoryInput):
    return save_memory(
        company_id=payload.company_id,
        category=payload.category,
        data=payload.data,
    )


@router.get("/{company_id}")
def read_memory(company_id: str):
    return get_memory(company_id)


@router.get("/{company_id}/recent")
def read_recent_memory(company_id: str):
    return get_recent_memory(company_id)


@router.get("/{company_id}/summary")
def read_memory_summary(company_id: str):
    return summarize_memory(company_id)