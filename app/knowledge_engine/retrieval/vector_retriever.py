from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class VectorRetriever:
    """
    Effectue une recherche vectorielle dans ChromaDB.
    """

    def __init__(self):

        self.embedding_service = (
            GeminiEmbeddingService()
        )

        self.vectorstore = (
            ChromaStore()
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        """
        Recherche les documents les plus proches
        de la question dans l'espace vectoriel.
        """

        embedding = (
            self.embedding_service.generate_query_embedding(
                query.question
            )
        )

        results = self.vectorstore.search(
            embedding=embedding,
            n_results=query.top_k,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        search_results: list[
            SearchResult
        ] = []

        for index, document in enumerate(
            documents
        ):

            metadata = {}

            if index < len(
                metadatas
            ):

                metadata = (
                    metadatas[index]
                )

            #
            # Chroma renvoie une distance.
            # Plus la distance est faible,
            # plus le document est pertinent.
            #

            distance = 0.0

            if index < len(
                distances
            ):

                distance = float(
                    distances[index]
                )

            #
            # Transformation de la distance
            # en score.
            #

            vector_score = max(
                0.0,
                1.0 - distance,
            )

            search_results.append(

                SearchResult(

                    document=document,

                    metadata=metadata,

                    vector_score=vector_score,

                    score=vector_score,

                    source="vector",
                )

            )

        return search_results
