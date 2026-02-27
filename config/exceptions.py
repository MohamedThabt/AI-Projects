import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")


# ──────────────────────────────────────────────
# Standard error response shape
# ──────────────────────────────────────────────

def _error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "status_code": status_code},
    )


# ──────────────────────────────────────────────
# Register all global exception handlers
# ──────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        messages = []
        for err in exc.errors():
            loc = " → ".join(str(part) for part in err["loc"])
            messages.append(f"{loc}: {err['msg']}")
        detail = "; ".join(messages)
        logger.warning("Validation error on %s %s — %s", request.method, request.url.path, detail)
        return _error_response(422, detail)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return _error_response(exc.status_code, exc.detail)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _error_response(500, "Internal server error")
