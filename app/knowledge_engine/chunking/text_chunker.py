from pathlib import Path


class TextChunker:
    """
    Découpe un fichier texte en morceaux.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
    ):

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_file(
        self,
        txt_path: Path,
    ) -> list[str]:

        if not txt_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {txt_path}"
            )

        text = txt_path.read_text(
            encoding="utf-8"
        )

        return self.chunk_text(
            text
        )

    def chunk_text(
        self,
        text: str,
    ) -> list[str]:

        text = " ".join(
            text.split()
        )

        chunks = []

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[
                start:end
            ].strip()

            if chunk:

                chunks.append(
                    chunk
                )

            start += (
                self.chunk_size
                - self.overlap
            )

        return chunks
