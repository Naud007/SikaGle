import requests
from pathlib import Path

from app.knowledge_engine.config import config


class FAODatasetsDownloader:

    def __init__(self):

        self.storage_dir = (
            config.raw_dir
            / "fao"
            / "datasets"
        )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def download(
        self,
        url: str,
        filename: str
    ):

        print(
            f"[FAO DATASET] "
            f"Téléchargement : {filename}"
        )

        response = requests.get(
            url,
            timeout=120
        )

        response.raise_for_status()

        file_path = (
            self.storage_dir
            / filename
        )

        file_path.write_bytes(
            response.content
        )

        print(
            f"[FAO DATASET] "
            f"Enregistré : {file_path}"
        )

        return file_path
