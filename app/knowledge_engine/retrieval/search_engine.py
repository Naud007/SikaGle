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

    # =========================================================
    # FUSION DES RÉSULTATS
    # =========================================================

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

            merged[
                self._key(result)
            ] = result

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

        results = list(
            merged.values()
        )

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
            results
        )

        # =====================================================
        # TRI
        # =====================================================

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[
            :query.top_k
        ]

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

            metadata = (
                result.metadata or {}
            )

            # =================================================
            # SOURCE
            # =================================================

            if query.source:

                source = str(
                    metadata.get(
                        "source",
                        "",
                    )
                )

                if (
                    source.lower()
                    != query.source.lower()
                ):

                    continue

            # =================================================
            # LANGUE
            # =================================================

            if query.language:

                language = str(
                    metadata.get(
                        "language",
                        "",
                    )
                )

                if (
                    language.lower()
                    != query.language.lower()
                ):

                    continue

            # =================================================
            # TYPE DOCUMENT
            # =================================================

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

            # =================================================
            # ANNÉE
            # =================================================

            if (
                query.publication_year
                is not None
            ):

                try:

                    year = int(
                        metadata.get(
                            "publication_year",
                            metadata.get(
                                "published_at"
                            ),
                        )
                    )

                except Exception:

                    continue

                if (
                    year
                    != query.publication_year
                ):

                    continue

            filtered.append(
                result
            )

        return filtered

    # =========================================================
    # RE-RANKING
    # =========================================================

    def rerank(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """
        Recalcule le score global de chaque résultat.
        """

        for result in results:

            result.score = (
                self.compute_score(
                    result
                )
            )

        return results

    # =========================================================
    # SCORE FINAL
    # =========================================================

    def compute_score(
        self,
        result: SearchResult,
    ) -> float:
        """
        Calcule le score final d'un document/chunk.
        """

        metadata = (
            result.metadata or {}
        )

        score = 0.0

        # =====================================================
        # SIMILARITÉ VECTORIELLE
        # =====================================================

        score += (
            result.vector_score * 10
        )

        # =====================================================
        # RECHERCHE LEXICALE
        # =====================================================

        score += (
            result.keyword_score * 2
        )

        # =====================================================
        # BONUS LANGUE FRANÇAISE
        # =====================================================

        language = str(
            metadata.get(
                "language",
                "",
            )
        ).lower()

        if language == "fr":

            score += 1

        # =====================================================
        # BONUS RÉCENCE
        # =====================================================

        try:

            publication_year = (
                metadata.get(
                    "publication_year"
                )
            )

            if publication_year is None:

                published_at = metadata.get(
                    "published_at"
                )

                if published_at:

                    publication_year = (
                        str(
                            published_at
                        )[:4]
                    )

            year = int(
                publication_year
            )

            current_year = (
                datetime.now().year
            )

            age = (
                current_year - year
            )

            if age <= 2:

                score += 3

            elif age <= 5:

                score += 2

            elif age <= 10:

                score += 1

        except Exception:

            pass

        # =====================================================
        # DÉTAILS DU CLASSEMENT
        # =====================================================

        result.ranking_details = {

            "vector_score":
                result.vector_score,

            "keyword_score":
                result.keyword_score,

            "language_bonus":
                (
                    1
                    if language == "fr"
                    else 0
                ),

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

        IMPORTANT :
        Un même document peut contenir plusieurs chunks.
        L'identifiant du document seul ne doit donc PAS
        être utilisé comme clé.

        La combinaison :

            document + chunk_index

        permet de conserver chaque chunk séparément.
        """

        metadata = (
            result.metadata or {}
        )

        document_id = (
            metadata.get(
                "document"
            )
            or metadata.get(
                "document_id"
            )
            or metadata.get(
                "identifier"
            )
            or result.document[:80]
        )

        chunk_index = (
            metadata.get(
                "chunk_index"
            )
        )

        if chunk_index is not None:

            return (
                f"{document_id}"
                f"::chunk::{chunk_index}"
            )

        return str(
            document_id
        )