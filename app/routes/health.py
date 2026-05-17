from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "Norbee AI",
        "version": "1.0.0"
    }