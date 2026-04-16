from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.config import settings
from app.db import database_backend, engine

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    show_dev_setup_hint = settings.environment.lower() == "development"
    return templates.TemplateResponse(
        request,
        "landing.html",
        {"request": request, "show_dev_setup_hint": show_dev_setup_hint},
    )


@router.get("/healthz", response_model=None)
def healthz() -> JSONResponse | dict[str, str]:
    db_kind = database_backend()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — surface any DB error to operators
        msg = str(exc).replace("\n", " ")[:240]
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "database": db_kind,
                "database_status": f"unreachable: {msg}",
            },
        )
    return {
        "status": "ok",
        "database": db_kind,
        "database_status": "connected",
    }
