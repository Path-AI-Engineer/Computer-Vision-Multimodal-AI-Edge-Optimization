from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.errors import CapabilityUnavailableError, capability_handler

app = FastAPI(
    title="Document Vision OCR Extractor API",
    version="1.0.0-rc.1",
    description=(
        "Evidence-first OCR and key information extraction for single-page receipts. "
        "Bundled samples are qualification fixtures, not SROIE."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_exception_handler(CapabilityUnavailableError, capability_handler)  # type: ignore[arg-type]
app.include_router(router)

samples = settings.root / "data" / "samples"
if samples.exists():
    app.mount("/assets/samples", StaticFiles(directory=samples), name="sample-assets")

frontend = settings.root / "frontend" / "dist"
if frontend.exists():
    assets = frontend / "assets"
    if assets.exists():
        app.mount("/app/assets", StaticFiles(directory=assets), name="frontend-assets")

    @app.get("/app/{path:path}", include_in_schema=False)
    def application(path: str) -> FileResponse:
        candidate = (frontend / path).resolve()
        if path and candidate.is_file() and frontend.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(frontend / "index.html")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/app/")
