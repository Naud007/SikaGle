"""
SikaGlé

Rapport synthétique de l'état de la sécurité.
"""

from dataclasses import dataclass


@dataclass
class SecurityReport:
    """
    Représente l'état des principaux mécanismes
    de sécurité de la plateforme.
    """

    secret_validation: bool

    rate_limiting: bool

    security_headers: bool

    input_validation: bool
