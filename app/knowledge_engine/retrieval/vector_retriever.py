from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class VectorRetriever:
    """
    Recherche vectorielle dans ChromaDB.
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
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:

        embedding = (
            self.embedding_service.generate_query_embedding(
                query
            )
        )

        results = self.vectorstore.search(
            embedding=embedding,
            n_results=top_k,
        )

        documents = (
            results.get(
                "documents",
                [[]],
            )[0]
        )

        metadatas = (
            results.get(
                "metadatas",
                [[]],
            )[0]
        )

        distances = (
            results.get(
                "distances",
                [[]],
            )[0]
        )

        search_results = []

        for i, document in enumerate(
            documents
        ):

            score = 0.0

            if i < len(
                distances
            ):
                score = distances[i]

            metadata = {}

            if i < len(
                metadatas
            ):
                metadata = (
                    metadatas[i]
                )

            search_results.append(

                SearchResult(

                    document=document,

                    metadata=metadata,

                    score=score,

                    source="vector",
                )
            )

        return search_results
