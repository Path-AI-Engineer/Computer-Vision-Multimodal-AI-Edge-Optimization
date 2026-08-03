from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from edge_ai.registry.service import RegistryError


async def registry_error_handler(_: Request, error: RegistryError) -> JSONResponse:
    return JSONResponse(
        status_code=404, content={"code": "VARIANT_NOT_FOUND", "detail": str(error)}
    )


async def value_error_handler(_: Request, error: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=422, content={"code": "VALIDATION_FAILED", "detail": str(error)}
    )
