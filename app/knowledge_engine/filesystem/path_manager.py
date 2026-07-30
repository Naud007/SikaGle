from pathlib import Path


class PathManager:
    """
    Gère tous les chemins du système de fichiers du Knowledge Engine.
    """

    def __init__(
        self,
        root: Path | None = None,
    ) -> None:

        self.root = root or Path("data")

    def pdf_directory(
        self,
        source: str,
    ) -> Path:
        """
        Retourne le dossier des PDF d'une source.
        """

        path = (
            self.root
            / "pdfs"
            / source.lower()
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def pdf_path(
        self,
        source: str,
        filename: str,
    ) -> Path:
        """
        Retourne le chemin complet d'un PDF.
        """

        return (
            self.pdf_directory(source)
            / filename
        )

    def text_directory(
        self,
    ) -> Path:
        """
        Retourne le dossier des textes extraits.
        """

        path = (
            self.root
            / "texts"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def cache_directory(
        self,
    ) -> Path:
        """
        Retourne le dossier du cache.
        """

        path = (
            self.root
            / "cache"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    def logs_directory(
        self,
    ) -> Path:
        """
        Retourne le dossier des logs.
        """

        path = (
            self.root
            / "logs"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path
