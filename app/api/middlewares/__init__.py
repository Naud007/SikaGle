"""
Middlewares de l'API SikaGlé.
"""

from .security_headers import (
    SecurityHeadersMiddleware,
)

__all__ = [
    "SecurityHeadersMiddleware",
]
