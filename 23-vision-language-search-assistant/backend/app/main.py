from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from assistant.guardrails.policy import GuardrailViolation
from backend.app.api.router import router
from backend.app.core.config import settings
from backend.app.core.errors import guardrail_handler

app = FastAPI(
    title="Vision-Language Retrieval Studio API",
    version="1.0.0-rc.1",
    description=(
        "Evidence-grounded text, image and conversational retrieval. The bundled corpus "
        "is a qualification fixture and is not presented as Flickr8k or an official CLIP benchmark."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
app.add_exception_handler(GuardrailViolation, guardrail_handler)  # type: ignore[arg-type]
app.include_router(router)

corpus_assets = settings.root / "data" / "samples"
if corpus_assets.exists():
    app.mount("/assets/corpus", StaticFiles(directory=corpus_assets), name="corpus-assets")

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
