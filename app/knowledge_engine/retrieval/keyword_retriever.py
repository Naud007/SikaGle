from pathlib import Path

from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class KeywordRetriever:

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
        query: SearchQuery,
    ) -> list[SearchResult]:

        keywords = [

            word.lower()

            for word in query.question.split()

            if len(word) >= 3
        ]

        results = []

        if not self.text_directory.exists():

            return results

        for txt_file in self.text_directory.glob(
            "*.txt"
        ):

            text = txt_file.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            lower = text.lower()

            score = sum(

                lower.count(keyword)

                for keyword in keywords
            )

            if score == 0:
                continue

            results.append(

                SearchResult(

                    document=text[:700],

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

        return results[: query.top_k]
