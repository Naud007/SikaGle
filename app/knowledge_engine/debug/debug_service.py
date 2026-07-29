from __future__ import annotations

from pathlib import Path

import fitz

from app.knowledge_engine.chunking import TextChunker


class DebugService:
    """
    Service de diagnostic de la chaîne d'ingestion.

    Il permet d'inspecter rapidement un document PDF
    avant son indexation.
    """

    def __init__(self):
        self.chunker = TextChunker()

    def inspect_pdf(
        self,
        pdf_path: Path,
    ) -> dict:

        report = {
            "file": pdf_path.name,
            "exists": pdf_path.exists(),
        }

        if not pdf_path.exists():
            return report

        report["size_bytes"] = pdf_path.stat().st_size

        document = fitz.open(pdf_path)

        try:

            pages = []

            for page in document:
                text = page.get_text("text")

                if text:
                    pages.append(text)

            full_text = "\n\n".join(pages)

        finally:
            document.close()

        chunks = self.chunker.chunk_text(
            full_text
        )

        report.update(
            {
                "pages": len(pages),
                "characters": len(full_text),
                "chunks": len(chunks),
            }
        )

        return report
