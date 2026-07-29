from pathlib import Path

import fitz


class PDFExtractor:
    """
    Extrait le texte d'un document PDF.
    """

    @staticmethod
    def extract(pdf_path: Path) -> str:
        """
        Extrait tout le texte d'un PDF.

        Args:
            pdf_path: Chemin du fichier PDF.

        Returns:
            Le texte complet du document.
        """

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF introuvable : {pdf_path}"
            )

        document = fitz.open(pdf_path)

        try:
            pages = []

            for page in document:
                text = page.get_text("text")

                if text:
                    pages.append(text.strip())

            return "\n\n".join(pages)

        finally:
            document.close()
