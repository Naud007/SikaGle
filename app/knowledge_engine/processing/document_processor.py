from pathlib import Path

from app.knowledge_engine.extraction import PDFExtractor


class DocumentProcessor:
    """
    Pipeline de traitement d'un document PDF.
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

    def process(
        self,
        pdf_path: Path,
    ) -> Path:
        """
        PDF
            ↓
        Extraction
            ↓
        Nettoyage
            ↓
        Sauvegarde TXT
        """

        text = PDFExtractor.extract(
            pdf_path
        )

        cleaned_text = self._clean_text(
            text
        )

        output_path = (
            self.output_dir
            / f"{pdf_path.stem}.txt"
        )

        output_path.write_text(
            cleaned_text,
            encoding="utf-8",
        )

        return output_path

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
