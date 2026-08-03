from __future__ import annotations

from io import BytesIO

import numpy as np
from fastapi import APIRouter, HTTPException, Request, Response
from PIL import Image, UnidentifiedImageError

from assistant.guardrails.policy import validate_message
from backend.app.core.config import settings
from backend.app.schemas.resources import (
    ImageSearchResource,
    SessionCreateResource,
    SessionMessageResource,
    TextSearchResource,
)
from backend.app.services.runtime import Runtime

router = APIRouter()
runtime = Runtime.load(settings.root, settings.session_ttl_seconds)


async def _bounded_body(request: Request) -> bytes:
    payload = bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload) > settings.max_upload_bytes:
            raise HTTPException(413, "The image exceeds the configured upload limit.")
    return bytes(payload)


@router.get("/health", tags=["runtime"])
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "vision-language-search-assistant"}


@router.get("/ready", tags=["runtime"])
def ready() -> dict[str, str | int]:
    return {
        "status": "ready",
        "bundle": "vision-language-qualification-v1",
        "corpus_images": len(runtime.retrieval.items),
    }


@router.get("/v1/models/current", tags=["model"])
def current_model() -> dict:
    return runtime.json_artifact("artifacts", "bundles", "vision-language-qualification-v1.json")


@router.get("/v1/indexes/current", tags=["index"])
def current_index() -> dict:
    return runtime.json_artifact("artifacts", "indexes", "index-manifest.json")


@router.get("/v1/corpus", tags=["search"])
def corpus() -> dict:
    return {
        "dataset": "sealed-visual-retrieval-qualification-v1",
        "items": [
            {
                **item.to_dict(),
                "image_url": f"/assets/corpus/{item.filename}",
            }
            for item in runtime.retrieval.items
        ],
    }


@router.post("/v1/search/text", tags=["search"])
def search_text(resource: TextSearchResource) -> dict:
    query = validate_message(resource.query)
    filters: dict[str, str | bool] = {}
    if resource.category:
        filters["category"] = resource.category
    if resource.color:
        filters["color"] = resource.color
    if resource.has_people is not None:
        filters["has_people"] = resource.has_people
    return runtime.retrieval.search_text(
        query,
        mode=resource.mode,
        index_mode=resource.index_mode,
        top_k=resource.top_k,
        alpha=resource.alpha,
        negative_terms=tuple(resource.negative_terms),
        filters=filters,
    ).to_dict()


@router.post("/v1/search/image", tags=["search"])
def search_image(resource: ImageSearchResource) -> dict:
    try:
        response = runtime.retrieval.search_image(
            resource.image_id,
            index_mode=resource.index_mode,
            top_k=resource.top_k,
        )
    except KeyError as error:
        raise HTTPException(404, f"Unknown corpus image: {resource.image_id}") from error
    return response.to_dict()


@router.post("/v1/search/image-upload", tags=["search"])
async def search_image_upload(request: Request) -> dict:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Use a JPEG, PNG or WebP image.")
    payload = await _bounded_body(request)
    try:
        image = Image.open(BytesIO(payload)).convert("RGB").resize((64, 64))
        pixels = np.asarray(image, dtype=np.float32) / 255.0
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(422, "The uploaded image could not be decoded.") from error
    red, green, blue = pixels.mean(axis=(0, 1))
    brightness = float(pixels.mean())
    vector = np.zeros(12, dtype=np.float32)
    vector[8] = max(float(red - blue), 0.05)
    vector[9] = max(float(max(green, blue) - red), 0.05)
    vector[4] = max(float(green - 0.3), 0.0)
    vector[7] = max(0.5 - brightness, 0.0)
    response = runtime.retrieval.search_vector(vector, query_label="uploaded color composition")
    result = response.to_dict()
    result["upload_boundary"] = (
        "Upload qualification uses a documented color-composition adapter, not CLIP. "
        "It validates upload, ranking and evidence contracts only."
    )
    return result


@router.post("/v1/sessions", tags=["assistant"])
def create_session(resource: SessionCreateResource, response: Response) -> dict:
    state = runtime.sessions.create(resource.top_k, resource.mode, resource.index_mode)
    response.status_code = 201
    return {"state": state.to_dict(), "expires_in_seconds": settings.session_ttl_seconds}


@router.post("/v1/sessions/{session_id}/messages", tags=["assistant"])
def session_message(session_id: str, resource: SessionMessageResource) -> dict:
    state = runtime.sessions.get(session_id)
    if state is None:
        raise HTTPException(404, "The session does not exist or has expired.")
    return runtime.assistant.handle(state, resource.message)


@router.delete("/v1/sessions/{session_id}", tags=["assistant"])
def delete_session(session_id: str) -> Response:
    if not runtime.sessions.delete(session_id):
        raise HTTPException(404, "The session does not exist or has expired.")
    return Response(status_code=204)


@router.get("/v1/evaluation/summary", tags=["evaluation"])
def evaluation_summary() -> dict:
    return runtime.json_artifact("reports", "metrics", "retrieval-metrics.json")


@router.get("/v1/evaluation/index", tags=["evaluation"])
def index_benchmark() -> dict:
    return runtime.json_artifact("reports", "metrics", "index-benchmark.json")


@router.get("/v1/evaluation/conversations", tags=["evaluation"])
def conversational_evaluation() -> dict:
    return runtime.json_artifact("reports", "metrics", "conversational-eval.json")


@router.get("/v1/evaluation/errors", tags=["evaluation"])
def evaluation_errors() -> dict:
    return runtime.json_artifact("reports", "errors", "error-gallery.json")
