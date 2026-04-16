from fastapi import APIRouter

from app.api.v1 import (
    annotation_routes,
    categories,
    media_assets,
    meta,
    sub_categories,
    sub_sub_categories,
    subject_pages,
)

api_router = APIRouter()
api_router.include_router(meta.router)
api_router.include_router(categories.router, prefix="/categories")
api_router.include_router(sub_categories.router, prefix="/sub-categories")
api_router.include_router(sub_sub_categories.router, prefix="/sub-sub-categories")
api_router.include_router(subject_pages.router, prefix="/subject-pages")
api_router.include_router(annotation_routes.router)
api_router.include_router(media_assets.router)
