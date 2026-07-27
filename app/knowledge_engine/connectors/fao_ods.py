import requests


class FAOODSDownloader:

    def __init__(self):

        self.source_name = "fao_agris_ods"

        self.download_url = (
            "https://agris.fao.org/ods/AGRIS.ODS.xml"
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; "
                "SikaGle-KnowledgeEngine/2.0)"
            )
        }


    # =========================================================
    # TÉLÉCHARGER AGRIS ODS EN MÉMOIRE
    # =========================================================

    def download(self):

        print(
            "[FAO ODS] Téléchargement "
            "AGRIS.ODS.xml en mémoire..."
        )

        response = requests.get(
            self.download_url,
            headers=self.headers,
            timeout=120
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
        )

        response.raise_for_status()

        content = response.content

        print(
            "[FAO ODS] Téléchargement terminé."
        )

        print(
            "[FAO ODS] Taille :",
            len(content),
            "octets"
        )

        return {
            "filename": "AGRIS.ODS.xml",
            "url": self.download_url,
            "content": content
        }


# =============================================================
# TEST
# =============================================================

def test_fao_ods():

    print("=" * 50)

    print(
        "SikaGlé - Test FAO AGRIS ODS en mémoire"
    )

    print("=" * 50)

    try:

        downloader = FAOODSDownloader()

        dataset = downloader.download()

        return {
            "status": "success",
            "filename": dataset["filename"],
            "url": dataset["url"],
            "size": len(
                dataset["content"]
            )
        }

    except Exception as e:

        print(
            "❌ Erreur téléchargement AGRIS ODS :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }
