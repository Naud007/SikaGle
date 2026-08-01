from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RegionalKnowledge:

    department: str

    common_crops: list[str] = field(
        default_factory=list
    )

    common_diseases: list[str] = field(
        default_factory=list
    )

    common_pests: list[str] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )
