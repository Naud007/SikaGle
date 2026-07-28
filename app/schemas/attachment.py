from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, HttpUrl


class DocumentAttachment(BaseModel):
    """
    Représente un fichier associé à un document.
    """

    filename: Optional[str] = None

    url: HttpUrl

    mime_type: Optional[str] = None

    file_type: Optional[str] = None

    local_path: Optional[str] = None

    checksum: Optional[str] = None
