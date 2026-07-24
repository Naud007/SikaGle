import requests
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

        self.file_path = (
            self.download_dir
            / "agris_ods_download"
        )

        self.download_url = (
            "https://www.fao.org/agris/"
        )

    def download(self):

        print(
            "[FAO ODS] Accès à la page officielle AGRIS..."
        )

        response = requests.get(
            self.download_url,
            timeout=120,
            headers={
                "User-Agent":
                "Mozilla/5.0 "
                "(compatible; SikaGle-KnowledgeEngine/1.0)"
            }
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            ""
        )

        print(
            "[FAO ODS] Type de contenu :",
            content_type
        )

        print(
            "[FAO ODS] Taille réponse :",
            len(response.content),
            "octets"
        )

        # Pour l'instant, on sauvegarde la réponse
        # afin d'analyser la structure réelle de la page.
        with open(
            self.file_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        print(
            "[FAO ODS] Réponse sauvegardée :",
            self.file_path
        )

        return self.file_path


def test_fao_ods():

    downloader = FAOODSDownloader()

    try:

        file_path = downloader.download()

        print(
            "✅ Connexion AGRIS réussie :",
            file_path
        )

        return file_path

    except Exception as e:

        print(
            "❌ Erreur FAO AGRIS ODS :",
            e
        )

        return None
