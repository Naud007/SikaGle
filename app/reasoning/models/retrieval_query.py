from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievalQuery:

    crop: str | None = None

    symptoms: list[str] = field(
        default_factory=list
    )

    intent: str | None = None

    location: str | None = None

    keywords: list[str] = field(
        default_factory=list
    )
