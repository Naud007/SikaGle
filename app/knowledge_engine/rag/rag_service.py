from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class RAGService:
    """
    Recherche les passages les plus pertinents
    dans la base vectorielle.
    """

    def __init__(self):

        self.embedding = GeminiEmbeddingService()

        self.vectorstore = ChromaStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ):

        query_embedding = (
            self.embedding.generate_query_embedding(
                question
            )
        )

        return self.vectorstore.search(
            embedding=query_embedding,
            n_results=top_k,
        )
