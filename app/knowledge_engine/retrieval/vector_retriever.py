import time

from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.repositories import (
    KnowledgeRepository,
)
from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class VectorRetriever:
    """
    Effectue une recherche vectorielle dans la base documentaire.

    Le retriever ne dépend plus directement de ChromaDB.
    Toute la persistance est déléguée au KnowledgeRepository.
    """

    def __init__(self):

        self.embedding_service = (
            GeminiEmbeddingService()
        )

        self.repository = (
            KnowledgeRepository()
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        """
        Recherche les documents les plus proches
        de la question.
        """

        start_embedding = time.time()

        embedding = (
            self.embedding_service.generate_query_embedding(
                query.question
            )
        )

        print(
            "⏱️ [TIMING] Embedding Jina (recherche vectorielle) : "
            f"{time.time() - start_embedding:.2f}s"
        )

        start_supabase = time.time()

        results = self.repository.search(
            embedding=embedding,
            top_k=query.top_k,
        )

        print(
            "⏱️ [TIMING] Requête Supabase vectorielle : "
            f"{time.time() - start_supabase:.2f}s"
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

            distance = 0.0

            if index < len(
                distances
            ):

                distance = float(
                    distances[index]
                )

            #
            # Conversion de la distance vectorielle
            # en score de similarité.
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