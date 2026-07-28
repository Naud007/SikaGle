from __future__ import annotations

from pathlib import Path

import requests


class Downloader:
    """
    Télécharge un fichier depuis une URL.
    """

    def download_file(
        self,
        url: str,
        destination: Path,
    ) -> Path:

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        response = requests.get(
            url,
            stream=True,
            timeout=60,
            allow_redirects=True,
        )

        response.raise_for_status()

        with destination.open("wb") as file:

            for chunk in response.iter_content(
                chunk_size=8192,
            ):

                if chunk:
                    file.write(chunk)

        return destination
