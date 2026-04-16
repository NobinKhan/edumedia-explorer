from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/meta")
def read_meta() -> dict[str, str]:
    return {"name": "EduMedia Author", "api_version": "v1"}
