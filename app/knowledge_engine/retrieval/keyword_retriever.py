from pathlib import Path

from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class KeywordRetriever:
    """
    Recherche simple par mots-clés
    dans les fichiers texte.
    """

    def __init__(
        self,
        text_directory: Path | None = None,
    ):

        self.text_directory = (
            text_directory
            or Path("data/texts")
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:

        keywords = [

            word.lower()

            for word in query.split()

            if len(word) >= 3
        ]

        results = []

        if not self.text_directory.exists():

            return results

        for txt_file in sorted(
            self.text_directory.glob("*.txt")
        ):

            text = txt_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            lower_text = text.lower()

            score = sum(

                lower_text.count(
                    keyword
                )

                for keyword in keywords
            )

            if score == 0:
                continue

            excerpt = self._excerpt(
                text,
                keywords,
            )

            results.append(

                SearchResult(

                    document=excerpt,

                    metadata={
                        "document": txt_file.stem,
                    },

                    score=float(score),

                    source="keyword",
                )
            )

        results.sort(

            key=lambda r: r.score,

            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def _excerpt(
        text: str,
        keywords: list[str],
        size: int = 700,
    ) -> str:

        lower = text.lower()

        for keyword in keywords:

            index = lower.find(
                keyword
            )

            if index != -1:

                start = max(
                    0,
                    index - 250,
                )

                end = min(
                    len(text),
                    start + size,
                )

                return text[
                    start:end
                ]

        return text[:size]
