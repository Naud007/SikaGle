import requests
from pathlib import Path

from app.knowledge_engine.config import config


class FAOODSDownloader:

    def __init__(self):

        self.source_name = "fao_agris_ods"

        self.download_dir = (
            config.raw_dir
            / "fao"
            / "ods"
        )

        self.download_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.download_url = (
            "https://agris.fao.org/ods/AGRIS.ODS.xml"
        )

        self.file_path = (
            self.download_dir
            / "AGRIS.ODS.xml"
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; "
                "SikaGle-KnowledgeEngine/1.0)"
            )
        }

    def download(self):

        print(
            "[FAO ODS] Téléchargement "
            "du fichier AGRIS.ODS.xml..."
        )

        response = requests.get(
            self.download_url,
            headers=self.headers,
            timeout=600,
            stream=True
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
        )

        response.raise_for_status()

        total_size = 0

        with open(
            self.file_path,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    file.write(
                        chunk
                    )

                    total_size += len(
                        chunk
                    )

        print(
            "[FAO ODS] Téléchargement terminé."
        )

        print(
            "[FAO ODS] Taille du fichier :",
            total_size,
            "octets"
        )

        print(
            "[FAO ODS] Fichier enregistré :",
            self.file_path
        )

        return self.file_path


def test_fao_ods():

    print("=" * 50)

    print(
        "SikaGlé - Test téléchargement "
        "FAO AGRIS ODS"
    )

    print("=" * 50)

    downloader = FAOODSDownloader()

    try:

        file_path = downloader.download()

        if file_path and file_path.exists():

            print(
                "✅ Fichier AGRIS ODS téléchargé :",
                file_path
            )

            return {
                "status": "success",
                "file": str(
                    file_path
                )
            }

        print(
            "⚠️ Fichier non trouvé."
        )

        return {
            "status": "warning"
        }

    except Exception as e:

        print(
            "❌ Erreur téléchargement "
            "AGRIS ODS :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }
