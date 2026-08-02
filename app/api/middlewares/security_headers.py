"""
SikaGlé

Middleware ajoutant des en-têtes HTTP de sécurité.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Ajoute des en-têtes de sécurité à toutes les réponses.
    """

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = "no-referrer"

        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
