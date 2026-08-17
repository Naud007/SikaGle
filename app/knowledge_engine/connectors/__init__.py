from .base import BaseConnector
from .brab import BRABConnector
from .fao import FAOConnector
from .registry import registry


registry.register(
    "fao",
    FAOConnector,
)

registry.register(
    "brab",
    BRABConnector,
)


__all__ = [
    "BaseConnector",
    "FAOConnector",
    "BRABConnector",
    "registry",
]