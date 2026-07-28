from dataclasses import dataclass, field
from typing import Any


@dataclass
class OAIRecord:
    """
    Représente un enregistrement OAI-PMH.
    """

    identifier: str

    datestamp: str | None = None

    set_specs: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    raw_identifiers: list[str] = field(
        default_factory=list
    )
