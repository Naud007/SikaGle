import requests
import zipfile
from pathlib import Path

from app.knowledge_engine.config import config


class FAOODSDownloader:

    def __init__(self):

        self.source_name = "fao_agr_is_ods"

        self.download_dir = (
            config.raw_dir
            / "fao"
            / "ods"
        )

        self.download_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.zip_path = (
            self.download_dir
            / "agris_ods.zip"
        )

        self.extract_dir = (
            self.download_dir
            / "extracted"
        )

        self.extract_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Adresse officielle de téléchargement
        self.download_url = (
            "https://agris.fao.org/agris_ods/"
        )

    def download(self):

        print(
            "[FAO ODS] Téléchargement "
            "de l'Open Data Set AGRIS..."
        )

        response = requests.get(
            self.download_url,
            timeout=300,
            headers={
                "User-Agent":
                "SikaGle-KnowledgeEngine/1.0"
            }
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
        )

        response.raise_for_status()

        with open(
            self.zip_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        print(
            "[FAO ODS] Fichier téléchargé :",
            self.zip_path
        )

        return self.zip_path

    def extract(self):

        if not self.zip_path.exists():

            raise FileNotFoundError(
                "Le fichier AGRIS ODS "
                "n'existe pas encore."
            )

        print(
            "[FAO ODS] Extraction "
            "des données..."
        )

        with zipfile.ZipFile(
            self.zip_path,
            "r"
        ) as zip_file:

            zip_file.extractall(
                self.extract_dir
            )

        print(
            "[FAO ODS] Extraction terminée :",
            self.extract_dir
        )

        return self.extract_dir
