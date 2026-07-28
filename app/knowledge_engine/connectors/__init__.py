from .base import BaseConnector
from .fao import FAOConnector
from .inrab import INRABConnector
from .registry import registry

registry.register("fao", FAOConnector)
registry.register("inrab", INRABConnector)

__all__ = [
    "BaseConnector",
    "FAOConnector",
    "INRABConnector",
    "registry",
]
