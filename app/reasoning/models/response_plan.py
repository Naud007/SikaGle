from __future__ import annotations

from dataclasses import dataclass, field

from app.reasoning.models.evidence import Evidence
from app.reasoning.models.hypothesis import Hypothesis


@dataclass
class ResponsePlan:

    summary: str

    main_hypothesis: Hypothesis

    secondary_hypotheses: list[
        Hypothesis
    ] = field(
        default_factory=list
    )

    evidences: list[
        Evidence
    ] = field(
        default_factory=list
    )

    recommendations: list[
        str
    ] = field(
        default_factory=list
    )
