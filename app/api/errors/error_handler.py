from fastapi import Request
from fastapi.responses import JSONResponse

from app.models.api_error import (
    ApiError,
)


class ErrorHandler:

    @staticmethod
    def build(
        status_code: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> JSONResponse:

        error = ApiError(
            code=code,
            message=message,
            details=details or {},
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                }
            },
        )

    @staticmethod
    async def exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:

        return ErrorHandler.build(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message=str(exc),
        )
