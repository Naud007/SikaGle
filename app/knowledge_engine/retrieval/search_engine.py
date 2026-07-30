from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class SearchEngine:
    """
    Moteur de fusion, filtrage et classement
    des résultats de recherche.
    """

    def merge(
        self,
        vector_results: list[SearchResult],
        keyword_results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        merged: dict[str, SearchResult] = {}

        #
        # Résultats vectoriels
        #

        for result in vector_results:

            merged[self._key(result)] = result

        #
        # Résultats keyword
        #

        for result in keyword_results:

            key = self._key(result)

            if key in merged:

                merged[key].score += result.score

            else:

                merged[key] = result

        results = list(merged.values())

        #
        # Application des filtres
        #

        results = self.apply_filters(
            results,
            query,
        )

        #
        # Tri
        #

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[: query.top_k]

    def apply_filters(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        filtered = []

        for result in results:

            metadata = result.metadata or {}

            #
            # Source
            #

            if query.source:

                source = str(
                    metadata.get(
                        "source",
                        "",
                    )
                )

                if source.lower() != query.source.lower():

                    continue

            #
            # Langue
            #

            if query.language:

                language = str(
                    metadata.get(
                        "language",
                        "",
                    )
                )

                if language.lower() != query.language.lower():

                    continue

            #
            # Type
            #

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

            #
            # Année
            #

            if query.publication_year is not None:

                year = metadata.get(
                    "publication_year"
                )

                try:

                    year = int(year)

                except Exception:

                    continue

                if year != query.publication_year:

                    continue

            filtered.append(result)

        return filtered

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
