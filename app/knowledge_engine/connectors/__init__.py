from .base import BaseConnector
from .brab import BRABConnector
from .fao import FAOConnector
from .africarice import AfricaRiceConnector
from .registry import registry

registry.register(
    "fao",
    FAOConnector,
)
registry.register(
    "brab",
    BRABConnector,
)
registry.register(
    "africarice",
    AfricaRiceConnector,
)

__all__ = [
    "BaseConnector",
    "FAOConnector",
    "BRABConnector",
    "AfricaRiceConnector",
    "registry",
]