from .base import BaseConnector
from .brab import BRABConnector
from .fao import FAOConnector
from .inrab import INRABConnector
from .registry import registry


registry.register(
    "fao",
    FAOConnector,
)

registry.register(
    "inrab",
    INRABConnector,
)

registry.register(
    "brab",
    BRABConnector,
)


__all__ = [
    "BaseConnector",
    "FAOConnector",
    "INRABConnector",
    "BRABConnector",
    "registry",
]
