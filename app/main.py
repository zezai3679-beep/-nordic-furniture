from __future__ import annotations

from fastapi import FastAPI

from app.config import settings
from app.routes.public import router as public_router
from app.services.repository import build_repository

app = FastAPI(title=settings.app_name)
app.state.repository = build_repository()
app.include_router(public_router)
