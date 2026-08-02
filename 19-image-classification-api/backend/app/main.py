from __future__ import annotations

from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import install_exception_handlers, router
from backend.app.core.config import settings
from backend.app.services.prediction_service import ArtifactUnavailableError, PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    prediction_service = PredictionService(settings)
    with suppress(ArtifactUnavailableError):
        prediction_service.load()
    app.state.prediction_service = prediction_service
    yield


app = FastAPI(
    title="Pet Breed Classification Studio API",
    version="1.0.0",
    description="Evidence-first fine-grained image classification service.",
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


samples = settings.root / "data" / "samples"
figures = settings.root / "reports" / "figures"
if samples.is_dir():
    app.mount("/samples", StaticFiles(directory=samples), name="samples")
if figures.is_dir():
    app.mount("/reports", StaticFiles(directory=figures), name="reports")

frontend = settings.root / "frontend" / "dist"
if frontend.is_dir():
    app.mount("/app", StaticFiles(directory=frontend, html=True), name="studio")
