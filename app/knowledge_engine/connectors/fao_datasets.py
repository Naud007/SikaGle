import requests


class FAODatasetsDownloader:

    def __init__(self):

        pass


    # =========================================================
    # TÉLÉCHARGER UN DATASET FAO EN MÉMOIRE
    # =========================================================

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

        content = response.content

        print(
            f"[FAO DATASET] "
            f"Dataset téléchargé en mémoire : "
            f"{filename} "
            f"({len(content)} octets)"
        )

        return {
            "filename": filename,
            "url": url,
            "content": content
        }
