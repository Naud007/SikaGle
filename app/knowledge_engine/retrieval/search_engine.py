from datetime import datetime

from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class SearchEngine:
    """
    Moteur de recherche documentaire.

    Responsabilités :
        - fusion des résultats
        - suppression des doublons
        - application des filtres
        - re-ranking
        - classement final
    """

    def merge(
        self,
        vector_results: list[SearchResult],
        keyword_results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        merged: dict[str, SearchResult] = {}

        # =====================================================
        # RÉSULTATS VECTORIELS
        # =====================================================

        for result in vector_results:
            merged[self._key(result)] = result

        # =====================================================
        # RÉSULTATS KEYWORD
        # =====================================================

        for result in keyword_results:

            key = self._key(result)

            if key in merged:

                merged[key].keyword_score = (
                    result.keyword_score
                )

            else:

                merged[key] = result

        results = list(merged.values())

        # =====================================================
        # FILTRES
        # =====================================================

        results = self.apply_filters(
            results,
            query,
        )

        # =====================================================
        # RE-RANKING
        # =====================================================

        results = self.rerank(
            results,
            query,
        )

        # =====================================================
        # TRI
        # =====================================================

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[:query.top_k]

    # =========================================================
    # FILTRES
    # =========================================================

    def apply_filters(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        filtered = []

        for result in results:

            metadata = result.metadata or {}

            # SOURCE
            if query.source:

                source = str(
                    metadata.get(
                        "source",
                        "",
                    )
                )

                if source.lower() != query.source.lower():
                    continue

            # LANGUE
            if query.language:

                language = str(
                    metadata.get(
                        "language",
                        "",
                    )
                )

                if language.lower() != query.language.lower():
                    continue

            # TYPE DOCUMENT
            if query.publication_type:

                publication_type = str(
                    metadata.get(
                        "publication_type",
                        metadata.get(
                            "document_type",
                            "",
                        ),
                    )
                )

                if (
                    publication_type.lower()
                    != query.publication_type.lower()
                ):
                    continue

            # ANNÉE
            if query.publication_year is not None:

                try:

                    year_value = metadata.get(
                        "publication_year"
                    )

                    if year_value is None:

                        year_value = metadata.get(
                            "published_at"
                        )

                    year = int(
                        str(year_value)[:4]
                    )

                except Exception:

                    continue

                if year != query.publication_year:
                    continue

            filtered.append(result)

        return filtered

    # =========================================================
    # RE-RANKING
    # =========================================================

    def rerank(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        for result in results:

            result.score = self.compute_score(
                result,
                query,
            )

        return results

    # =========================================================
    # SCORE FINAL
    # =========================================================

    def compute_score(
        self,
        result: SearchResult,
        query: SearchQuery,
    ) -> float:
        """
        Calcule le score final.

        Priorité :
        1. pertinence vectorielle
        2. correspondance avec la culture
        3. titre
        4. mots-clés
        5. contenu
        """

        metadata = result.metadata or {}

        question = query.question.lower()

        # =====================================================
        # TEXTE DU DOCUMENT
        # =====================================================

        title = str(
            metadata.get(
                "title",
                "",
            )
        ).lower()

        crop = str(
            metadata.get(
                "crop",
                "",
            )
        ).lower()

        culture = str(
            metadata.get(
                "culture",
                "",
            )
        ).lower()

        keywords = str(
            metadata.get(
                "keywords",
                "",
            )
        ).lower()

        document = str(
            result.document or ""
        ).lower()

        # =====================================================
        # MOTS IMPORTANTS
        # =====================================================

        important_words = [
            word.strip(
                ".,;:!?()[]{}'\""
            )
            for word in question.split()
            if len(
                word.strip(
                    ".,;:!?()[]{}'\""
                )
            ) >= 4
        ]

        # =====================================================
        # SCORE DE BASE
        # =====================================================

        score = 0.0

        # Le vectoriel reste la base principale.
        score += result.vector_score * 10

        # Le keyword intervient beaucoup moins.
        score += result.keyword_score * 0.75

        # =====================================================
        # CULTURE / PIMENT
        # =====================================================

        culture_match = False

        if "piment" in question:

            culture_match = (
                "piment" in crop
                or "piment" in culture
                or "pepper" in title
                or "capsicum" in title
                or "capsicum" in keywords
                or "capsicum" in document
                or "chilli" in title
                or "chilli" in document
            )

            if culture_match:
                score += 5.0
            else:
                score -= 3.0

        # =====================================================
        # TITRE
        # =====================================================

        title_matches = sum(
            1
            for word in important_words
            if word in title
        )

        score += min(
            title_matches * 1.5,
            4.5,
        )

        # =====================================================
        # MOTS-CLÉS
        # =====================================================

        keyword_matches = sum(
            1
            for word in important_words
            if word in keywords
        )

        score += min(
            keyword_matches * 1.0,
            3.0,
        )

        # =====================================================
        # CONTENU
        # =====================================================

        content_matches = sum(
            1
            for word in important_words
            if word in document
        )

        score += min(
            content_matches * 0.25,
            2.0,
        )

        # =====================================================
        # LANGUE
        # =====================================================

        language = str(
            metadata.get(
                "language",
                "",
            )
        ).lower()

        language_bonus = 0.0

        if language == "fr":

            language_bonus = 1.0

            score += language_bonus

        # =====================================================
        # RÉCENCE
        # =====================================================

        recency_bonus = 0.0

        try:

            publication_year = metadata.get(
                "publication_year"
            )

            if publication_year is None:

                published_at = metadata.get(
                    "published_at"
                )

                if published_at:

                    publication_year = str(
                        published_at
                    )[:4]

            year = int(
                str(publication_year)[:4]
            )

            current_year = datetime.now().year

            age = current_year - year

            if age <= 2:

                recency_bonus = 3.0

            elif age <= 5:

                recency_bonus = 2.0

            elif age <= 10:

                recency_bonus = 1.0

            score += recency_bonus

        except Exception:
            pass

        # =====================================================
        # DEBUG
        # =====================================================

        result.ranking_details = {

            "vector_score":
                result.vector_score,

            "keyword_score":
                result.keyword_score,

            "title_matches":
                title_matches,

            "keyword_matches":
                keyword_matches,

            "content_matches":
                content_matches,

            "culture_match":
                culture_match,

            "language_bonus":
                language_bonus,

            "recency_bonus":
                recency_bonus,

            "final_score":
                score,
        }

        return score

    # =========================================================
    # CLÉ UNIQUE D'UN CHUNK
    # =========================================================

    @staticmethod
    def _key(
        result: SearchResult,
    ) -> str:
        """
        Génère une clé unique pour un chunk.
        """

        metadata = result.metadata or {}

        document_id = (
            metadata.get("document")
            or metadata.get("document_id")
            or metadata.get("identifier")
            or result.document[:80]
        )

        chunk_index = metadata.get(
            "chunk_index"
        )

        if chunk_index is not None:

            return (
                f"{document_id}"
                f"::chunk::{chunk_index}"
            )

        return str(
            document_id
        )