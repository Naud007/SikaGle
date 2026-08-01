from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MissingInformation:

    field: str

    question: str

    required: bool = True
