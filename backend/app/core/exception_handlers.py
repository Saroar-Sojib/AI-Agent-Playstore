import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError

logger = logging.getLogger(__name__)


def register_exception_handlers(app):
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error("IntegrityError on %s: %s", request.url.path, exc, exc_info=True)
        if isinstance(exc.orig, ForeignKeyViolationError):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid foreign key reference"},
            )

        return JSONResponse(
            status_code=500,
            content={"detail": "Database integrity error"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exc()
        logger.error("Unhandled exception on %s:\n%s", request.url.path, tb)
        return JSONResponse(
            status_code=500,
            content={"detail": f"{type(exc).__name__}: {exc}"},
        )
