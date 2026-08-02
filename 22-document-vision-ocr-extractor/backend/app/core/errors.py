from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class CapabilityUnavailableError(RuntimeError):
    """A requested real capability is not present in the current runtime."""


def problem_response(status: int, title: str, detail: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": f"urn:document-vision:error:{code.lower()}",
            "title": title,
            "status": status,
            "detail": detail,
            "code": code,
        },
    )


async def capability_handler(_: Request, error: CapabilityUnavailableError) -> JSONResponse:
    return problem_response(503, "Capability unavailable", str(error), "OCR_RUNTIME_UNAVAILABLE")
