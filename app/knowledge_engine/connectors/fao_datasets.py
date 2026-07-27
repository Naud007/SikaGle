import requests


class FAODatasetsDownloader:

    def __init__(self):

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; "
                "SikaGle-KnowledgeEngine/1.0)"
            )
        }


    # =========================================================
    # TÉLÉCHARGER UN DATASET FAO EN MÉMOIRE
    # =========================================================

    def download(
        self,
        url: str,
        filename: str
    ):

        # =====================================================
        # VALIDATION
        # =====================================================

        if not url:

            raise ValueError(
                "URL du dataset manquante."
            )

        if not filename:

            raise ValueError(
                "Nom du dataset manquant."
            )


        url = str(
            url
        ).strip()

        filename = str(
            filename
        ).strip()


        print(
            "[FAO DATASET] "
            f"Téléchargement : {filename}"
        )

        print(
            "[FAO DATASET] "
            f"URL : {url}"
        )


        # =====================================================
        # TÉLÉCHARGEMENT HTTP
        # =====================================================

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=120
            )

            print(
                "[FAO DATASET] "
                f"Statut HTTP : "
                f"{response.status_code}"
            )

            response.raise_for_status()


            # =================================================
            # CONTENU EN MÉMOIRE
            # =================================================

            content = (
                response.content
            )


            if not content:

                raise RuntimeError(
                    "Le dataset téléchargé est vide."
                )


            print(
                "[FAO DATASET] "
                "Dataset téléchargé en mémoire : "
                f"{filename}"
            )

            print(
                "[FAO DATASET] "
                f"Taille : "
                f"{len(content)} octets"
            )


            # =================================================
            # RETOUR STANDARDISÉ
            # =================================================

            return {

                "filename":
                    filename,

                "url":
                    url,

                "content":
                    content,

                "content_type":
                    response.headers.get(
                        "Content-Type"
                    ),

                "size":
                    len(
                        content
                    )

            }


        except requests.RequestException as e:

            print(
                "[FAO DATASET] "
                f"Erreur HTTP : {e}"
            )

            raise


        except Exception as e:

            print(
                "[FAO DATASET] "
                f"Erreur téléchargement : {e}"
            )

            raise
