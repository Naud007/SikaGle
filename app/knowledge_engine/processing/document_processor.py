from pathlib import Path

from app.knowledge_engine.chunking import TextChunker
from app.knowledge_engine.extraction import PDFExtractor


class DocumentProcessor:
    """
    Pipeline complet de traitement d'un document.
    """

    def __init__(
        self,
        output_dir: Path | None = None,
    ):

        self.output_dir = output_dir or Path(
            "data/texts"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.chunker = TextChunker()

    def process(
        self,
        pdf_path: Path,
    ) -> dict:

        # ============================
        # EXTRACTION
        # ============================

        text = PDFExtractor.extract(
            pdf_path
        )

        cleaned_text = self._clean_text(
            text
        )

        txt_path = (
            self.output_dir
            / f"{pdf_path.stem}.txt"
        )

        txt_path.write_text(
            cleaned_text,
            encoding="utf-8",
        )

        # ============================
        # CHUNKING
        # ============================

        chunks = self.chunker.chunk_text(
            cleaned_text
        )

        return {
            "txt_path": txt_path,
            "chunks": chunks,
            "chunks_count": len(chunks),
            "characters": len(cleaned_text),
        }

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        lines = []

        for line in text.splitlines():

            line = " ".join(
                line.split()
            )

            if line:

                lines.append(
                    line
                )

        return "\n".join(
            lines
        )
