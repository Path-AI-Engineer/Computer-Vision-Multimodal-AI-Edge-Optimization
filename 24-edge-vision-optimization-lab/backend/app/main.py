from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.errors import registry_error_handler, value_error_handler
from edge_ai.registry.service import RegistryError

app = FastAPI(
    title="Edge Vision Benchmark Console API",
    version="1.0.0-rc.1",
    description=(
        "Measured qualification contracts for visual inference optimization. "
        "Qualification adapters are not presented as MobileNetV3, ONNX Runtime or physical "
        "edge results."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_exception_handler(RegistryError, registry_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValueError, value_error_handler)  # type: ignore[arg-type]
app.include_router(router)

sample_assets = settings.root / "data" / "samples"
if sample_assets.exists():
    app.mount("/assets/samples", StaticFiles(directory=sample_assets), name="sample-assets")

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
