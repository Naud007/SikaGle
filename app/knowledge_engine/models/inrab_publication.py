from dataclasses import dataclass
from typing import Optional

from .base_publication import BasePublication


@dataclass
class INRABPublication(BasePublication):
    """
    Publication provenant du portail INRAB.
    """

    domain: Optional[str] = None

    keywords: Optional[list[str]] = None
