from fastapi import APIRouter

from app.api.v1 import ingestion, qa, selection

api_router = APIRouter()

api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(selection.router, prefix="/selection", tags=["selection"])
