"""
SikaGlé

Types de sauvegarde de la plateforme.
"""

from enum import Enum


class BackupType(str, Enum):
    """
    Types de sauvegarde supportés.
    """

    DATABASE = "DATABASE"

    VECTORSTORE = "VECTORSTORE"

    DOCUMENTS = "DOCUMENTS"

    FULL = "FULL"
