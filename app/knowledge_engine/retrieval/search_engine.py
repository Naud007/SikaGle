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

            merged[
                self._key(result)
            ] = result

        # =====================================================
        # RÉSULTATS KEYWORD
        # =====================================================

        for result in keyword_results:

            key = self._key(result)

            if key in merged:

                # Le résultat vectoriel possède généralement
                # les métadonnées les plus complètes.
                #
                # On conserve donc le résultat vectoriel
                # et on lui ajoute uniquement le score lexical.

                merged_result = merged[key]

                merged_result.keyword_score = (
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
            : query.top_k
        ]

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
            # TYPE
            # =================================================

            if query.publication_type:

                publication_type = str(

                    metadata.get(
                        "publication_type",
                        "",
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
                            "publication_year"
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

    def compute_score(
        self,
        result: SearchResult,
    ) -> float:
        """
        Calcule le score final d'un document.
        """

        metadata = (
            result.metadata or {}
        )

        score = 0.0

        # =================================================
        # SIMILARITÉ VECTORIELLE
        # =================================================

        score += (
            result.vector_score * 10
        )

        # =================================================
        # RECHERCHE LEXICALE
        # =================================================

        score += (
            result.keyword_score * 2
        )

        # =================================================
        # BONUS LANGUE
        # =================================================

        language = str(

            metadata.get(
                "language",
                "",
            )

        ).lower()

        if language == "fr":

            score += 1

        # =================================================
        # BONUS RÉCENCE
        # =================================================

        try:

            year = int(

                metadata.get(
                    "publication_year"
                )

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

        # =================================================
        # DÉTAILS DE CLASSEMENT
        # =================================================

        result.ranking_details = {

            "vector_score":
                result.vector_score,

            "keyword_score":
                result.keyword_score,

            "language_bonus": (
                1
                if language == "fr"
                else 0
            ),

            "final_score":
                score,

        }

        return score

    @staticmethod
    def _key(
        result: SearchResult,
    ) -> str:

        metadata = (
            result.metadata or {}
        )

        # =================================================
        # IDENTIFIANT DOCUMENT
        # =================================================
        #
        # Chroma ajoute toujours "document"
        # lors de l'indexation.
        #
        # On privilégie donc "document" afin que
        # VectorRetriever et KeywordRetriever utilisent
        # exactement la même clé.

        document_id = metadata.get(
            "document"
        )

        if document_id:

            return str(
                document_id
            )

        # =================================================
        # IDENTIFIER
        # =================================================

        identifier = metadata.get(
            "identifier"
        )

        if identifier:

            return str(
                identifier
            )

        # =================================================
        # DERNIER RECOURS
        # =================================================

        return result.document[:80]