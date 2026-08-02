from __future__ import annotations

from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import install_exception_handlers, router
from backend.app.core.config import settings
from backend.app.services.detection_service import ArtifactUnavailableError, DetectionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    detection_service = DetectionService(settings)
    with suppress(ArtifactUnavailableError):
        detection_service.load()
    app.state.detection_service = detection_service
    yield


app = FastAPI(
    title="Retail Shelf Detection Console API",
    version="1.0.0",
    description="Dense single-class shelf object detection with explicit evidence profiles.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)
install_exception_handlers(app)


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse("/app/")


for route, directory, name in (
    ("/samples", settings.root / "data" / "samples", "samples"),
    ("/overlays", settings.root / "reports" / "figures", "overlays"),
):
    if directory.is_dir():
        app.mount(route, StaticFiles(directory=directory), name=name)

frontend = settings.root / "frontend" / "dist"
if frontend.is_dir():
    app.mount("/app", StaticFiles(directory=frontend, html=True), name="console")
