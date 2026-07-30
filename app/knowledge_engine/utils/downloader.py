from __future__ import annotations

from pathlib import Path

import requests


class Downloader:
    """
    Télécharge un fichier depuis une URL.
    """

    def inspect_url(
        self,
        url: str,
    ) -> dict:
        """
        Inspecte la réponse HTTP sans enregistrer le fichier.
        """

        response = requests.get(
            url,
            stream=True,
            timeout=60,
            allow_redirects=True,
        )

        first_bytes = b""

        try:
            first_bytes = next(
                response.iter_content(chunk_size=16)
            )
        except StopIteration:
            pass

        return {
            "requested_url": url,
            "final_url": response.url,
            "status_code": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "content_length": response.headers.get("Content-Length"),
            "pdf_signature": first_bytes.startswith(b"%PDF"),
            "first_bytes_hex": first_bytes.hex(),
        }

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
