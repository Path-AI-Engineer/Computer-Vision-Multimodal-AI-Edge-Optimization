from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import router
from backend.app.core.config import get_settings
from backend.app.services.quality_service import QualityControlService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.quality_service = QualityControlService(settings)
    yield


app = FastAPI(
    title="Surface Quality Control Lab API",
    version="1.0.0",
    description="Pixel segmentation and auditable piece-level quality decisions.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)

settings = get_settings()
frontend_root = settings.root / "frontend" / "dist"
data_root = settings.root / "data"
reports_root = settings.root / "reports"
if data_root.exists():
    app.mount("/evidence/data", StaticFiles(directory=data_root), name="evidence-data")
if reports_root.exists():
    app.mount("/evidence/reports", StaticFiles(directory=reports_root), name="evidence-reports")
if frontend_root.exists():
    app.mount("/app", StaticFiles(directory=frontend_root, html=True), name="app")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    target = "/app/" if Path(frontend_root).exists() else "/docs"
    return RedirectResponse(target)
