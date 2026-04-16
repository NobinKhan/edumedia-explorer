from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/editor", response_class=HTMLResponse)
def editor_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "editor_dashboard.html", {"request": request})


@router.get("/editor/pages/new", response_class=HTMLResponse)
def editor_new_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "editor_new.html", {"request": request})


@router.get("/editor/pages/{page_id}", response_class=HTMLResponse)
def editor_existing_page(page_id: int, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "editor_page.html", {"request": request, "page_id": page_id}
    )
