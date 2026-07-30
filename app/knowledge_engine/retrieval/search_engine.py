from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class SearchEngine:
    """
    Moteur de fusion et de classement des résultats.

    Cette classe centralise toute la logique métier
    de la recherche documentaire.
    """

    def merge(
        self,
        vector_results: list[SearchResult],
        keyword_results: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:

        merged: dict[str, SearchResult] = {}

        #
        # Résultats vectoriels
        #

        for result in vector_results:

            key = self._key(result)

            merged[key] = result

        #
        # Résultats keyword
        #

        for result in keyword_results:

            key = self._key(result)

            if key in merged:

                #
                # Bonus lorsqu'un document est retrouvé
                # par les deux méthodes.
                #

                merged[key].score += result.score

            else:

                merged[key] = result

        results = list(
            merged.values()
        )

        #
        # Classement
        #

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def _key(
        result: SearchResult,
    ) -> str:

        metadata = result.metadata or {}

        return str(

            metadata.get(

                "identifier",

                metadata.get(

                    "document",

                    result.document[:80],
                ),
            )
        )
