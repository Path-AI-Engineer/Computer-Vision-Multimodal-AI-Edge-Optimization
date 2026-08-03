from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from assistant.guardrails.policy import GuardrailViolation
from multimodal.data.manifest import ManifestError


async def guardrail_handler(_request: Request, error: GuardrailViolation) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "GUARDRAIL_REJECTED",
            "reason_code": error.reason_code,
            "detail": str(error),
        },
    )


async def manifest_handler(_request: Request, error: ManifestError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": "BUNDLE_INVALID", "detail": str(error)})
