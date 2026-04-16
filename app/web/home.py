from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

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


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
