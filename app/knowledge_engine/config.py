from pathlib import Path
from dataclasses import dataclass, field

# Racine du projet
BASE_DIR = Path(__file__).resolve().parents[2]

# Répertoire principal des connaissances
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


@dataclass
class KnowledgeEngineConfig:
    # Dossiers
    raw_dir: Path = KNOWLEDGE_DIR / "raw"
    processed_dir: Path = KNOWLEDGE_DIR / "processed"
    chunks_dir: Path = KNOWLEDGE_DIR / "chunks"
    archive_dir: Path = KNOWLEDGE_DIR / "archive"

    # Paramètres de traitement
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Fréquence de synchronisation
    sync_interval_hours: int = 24

    # Sources activées
    enabled_sources: list[str] = field(default_factory=lambda: [
        "brab",
        "inrab",
        "maep",
        "fao",
        "iita",
        "africarice",
    ])


config = KnowledgeEngineConfig()


# Création automatique des dossiers
for directory in [
    config.raw_dir,
    config.processed_dir,
    config.chunks_dir,
    config.archive_dir,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Création des sous-dossiers de chaque source
for source in config.enabled_sources:
    (config.raw_dir / source).mkdir(parents=True, exist_ok=True)
