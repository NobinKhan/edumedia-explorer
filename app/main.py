from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.db import engine
from app.models import Base
from app.services.media_service import _upload_root
from app.sqlite_maintenance import cancel_task, start_sqlite_auto_reset_task
from app.web import editor as editor_web
from app.web import home as home_web
from app.web import pages as pages_web


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _upload_root().mkdir(parents=True, exist_ok=True)
    reset_task = start_sqlite_auto_reset_task()
    try:
        yield
    finally:
        await cancel_task(reset_task)


app = FastAPI(title="EduMedia Author", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
_upload_root().mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(_upload_root())), name="uploads")

app.include_router(api_router, prefix="/api/v1")
app.include_router(home_web.router)
app.include_router(editor_web.router)
app.include_router(pages_web.router)
