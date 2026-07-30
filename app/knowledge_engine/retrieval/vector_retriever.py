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
        query: SearchQuery,
    ) -> list[SearchResult]:

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

        search_results = []

        for i, document in enumerate(documents):

            metadata = {}

            if i < len(metadatas):
                metadata = metadatas[i]

            score = 0.0

            if i < len(distances):
                score = distances[i]

            search_results.append(

                SearchResult(

                    document=document,

                    metadata=metadata,

                    score=score,

                    source="vector",
                )
            )

        return search_results
