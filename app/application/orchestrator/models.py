from dataclasses import dataclass
from typing import Any

from app.multimodal.models.input_message import InputMessage
from app.multimodal.models.output_message import OutputMessage


@dataclass
class PipelineRequest:
    """
    Requête entrant dans le pipeline.
    """

    input_message: InputMessage


@dataclass
class PipelineContext:
    """
    Contexte partagé entre les moteurs.
    """

    data: dict[str, Any]


@dataclass
class PipelineResult:
    """
    Résultat final du pipeline.
    """

    output_message: OutputMessage