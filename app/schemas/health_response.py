"""
Schémas de réponse des endpoints de santé de SikaGlé.
"""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Réponse de l'endpoint /health.
    """

    status: str
    service: str
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    """
    Réponse de l'endpoint /ready.
    """

    ready: bool
    database: bool
    knowledge_engine: bool
    timestamp: str


class LivenessResponse(BaseModel):
    """
    Réponse de l'endpoint /live.
    """

    alive: bool
    timestamp: str
