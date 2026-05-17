import os
from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str | None = Header(default=None)):
    expected_key = os.getenv("NORBEE_AI_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="NORBEE_AI_API_KEY is not configured.",
        )

    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )

    return True