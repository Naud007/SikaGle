from app.knowledge_engine.retrieval.keyword_retriever import (
    KeywordRetriever,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)
from app.knowledge_engine.retrieval.vector_retriever import (
    VectorRetriever,
)


class HybridRetriever:
    """
    Fusionne les recherches vectorielle
    et par mots-clés.
    """

    def __init__(self):

        self.vector = VectorRetriever()

        self.keyword = KeywordRetriever()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:

        vector_results = self.vector.search(
            query=query,
            top_k=top_k,
        )

        keyword_results = self.keyword.search(
            query=query,
            top_k=top_k,
        )

        merged: dict[str, SearchResult] = {}

        #
        # Résultats vectoriels
        #

        for result in vector_results:

            key = self._key(result)

            merged[key] = result

        #
        # Résultats mots-clés
        #

        for result in keyword_results:

            key = self._key(result)

            if key in merged:

                if result.score > merged[key].score:

                    merged[key] = result

            else:

                merged[key] = result

        results = list(
            merged.values()
        )

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def _key(
        result: SearchResult,
    ) -> str:
        """
        Identifiant unique d'un résultat.
        """

        metadata = result.metadata or {}

        return str(
            metadata.get(
                "document",
                result.document[:80],
            )
        )
