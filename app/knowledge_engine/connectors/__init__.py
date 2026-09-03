from .base import BaseConnector
from .brab import BRABConnector
from .fao import FAOConnector
from .africarice import AfricaRiceConnector
from .irri import IRRIConnector
from .bioversity import BioversityConnector
from .cifor import CIFORConnector
from .icrisat import ICRISATConnector
from .iita import IITAConnector
from .world_agroforestry import WorldAgroforestryConnector
from .iwmi import IWMIConnector
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
registry.register(
    "irri",
    IRRIConnector,
)
registry.register(
    "bioversity",
    BioversityConnector,
)
registry.register(
    "cifor",
    CIFORConnector,
)
registry.register(
    "icrisat",
    ICRISATConnector,
)
registry.register(
    "iita",
    IITAConnector,
)
registry.register(
    "world_agroforestry",
    WorldAgroforestryConnector,
)
registry.register(
    "iwmi",
    IWMIConnector,
)

__all__ = [
    "BaseConnector",
    "FAOConnector",
    "BRABConnector",
    "AfricaRiceConnector",
    "IRRIConnector",
    "BioversityConnector",
    "CIFORConnector",
    "ICRISATConnector",
    "IITAConnector",
    "WorldAgroforestryConnector",
    "IWMIConnector",
    "registry",
]