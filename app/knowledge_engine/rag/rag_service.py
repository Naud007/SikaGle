from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.rag.response_generator import (
    ResponseGenerator,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class RAGService:
    """
    Pipeline RAG complet :
    Question → Recherche → Génération.
    """

    def __init__(self):

        self.embedding = GeminiEmbeddingService()

        self.vectorstore = ChromaStore()

        self.generator = ResponseGenerator()

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:

        query_embedding = (
            self.embedding.generate_query_embedding(
                question
            )
        )

        results = self.vectorstore.search(
            embedding=query_embedding,
            n_results=top_k,
        )

        documents = []

        if (
            results.get("documents")
            and len(results["documents"]) > 0
        ):
            documents = results["documents"][0]

        metadatas = []

        if (
            results.get("metadatas")
            and len(results["metadatas"]) > 0
        ):
            metadatas = results["metadatas"][0]

        if not documents:

            return {
                "answer": (
                    "Je n'ai trouvé aucun document pertinent."
                ),
                "sources": [],
            }

        answer = self.generator.generate(
            question=question,
            contexts=documents,
        )

        return {
            "answer": answer,
            "sources": metadatas,
            "chunks_used": len(documents),
        }
