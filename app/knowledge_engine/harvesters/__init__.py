from app.knowledge_engine.harvesters.brab_oai import (
    BRABOAIHarvester,
)
from app.knowledge_engine.harvesters.registry import (
    HarvesterRegistry,
)

registry = HarvesterRegistry()

registry.register(
    "brab",
    BRABOAIHarvester,
)
