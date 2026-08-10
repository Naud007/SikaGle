from pathlib import Path

from app.knowledge_engine.repositories import (
    KnowledgeRepository,
)
from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class KeywordRetriever:
    """
    Recherche lexicale simple basée sur les fichiers texte
    extraits des documents PDF.

    Les métadonnées complètes sont récupérées depuis
    le KnowledgeRepository afin de rester cohérent
    avec la recherche vectorielle.
    """

    def __init__(
        self,
        text_directory: Path | None = None,
    ):

        self.text_directory = (
            text_directory
            or Path("data/texts")
        )

        self.repository = (
            KnowledgeRepository()
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        """
        Recherche les documents contenant les mots
        de la question.
        """

        if not self.text_directory.exists():

            return []

        keywords = self._extract_keywords(
            query.question
        )

        results: list[
            SearchResult
        ] = []

        for txt_file in self.text_directory.glob(
            "*.txt"
        ):

            try:

                text = txt_file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

            except Exception:

                continue

            score = self._keyword_score(
                text,
                keywords,
            )

            if score <= 0:

                continue

            # =================================================
            # RÉCUPÉRATION DES MÉTADONNÉES
            # =================================================

            metadata = {
                "document": txt_file.stem,
            }

            try:

                stored_document = (
                    self.repository.get_document(
                        txt_file.stem
                    )
                )

                stored_metadatas = (
                    stored_document.get(
                        "metadatas",
                        [],
                    )
                    or []
                )

                if stored_metadatas:

                    stored_metadata = (
                        stored_metadatas[0]
                        or {}
                    )

                    metadata.update(
                        stored_metadata
                    )

            except Exception:

                # Le résultat lexical reste utilisable
                # même si les métadonnées ne peuvent
                # pas être récupérées.
                pass

            # =================================================
            # RÉSULTAT
            # =================================================

            results.append(

                SearchResult(

                    document=text[:700],

                    metadata=metadata,

                    keyword_score=float(
                        score
                    ),

                    score=float(
                        score
                    ),

                    source="keyword",

                )

            )

        results.sort(

            key=lambda r:
                r.keyword_score,

            reverse=True,

        )

        return results[
            : query.top_k
        ]

    def _extract_keywords(
        self,
        question: str,
    ) -> list[str]:
        """
        Extrait les mots-clés de la question.
        """

        return [

            word.lower()

            for word in question.split()

            if len(word) >= 3

        ]

    def _keyword_score(
        self,
        text: str,
        keywords: list[str],
    ) -> int:
        """
        Calcule un score lexical simple.
        """

        lower = text.lower()

        score = 0

        for keyword in keywords:

            score += lower.count(
                keyword
            )

        return score