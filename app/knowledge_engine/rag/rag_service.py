from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.rag.response_generator import (
    ResponseGenerator,
)
from app.knowledge_engine.rag.source_formatter import (
    SourceFormatter,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class RAGService:
    """
    Pipeline RAG complet.

    Question
        ↓
    Embedding
        ↓
    Recherche Chroma
        ↓
    Génération de réponse
        ↓
    Formatage des sources
    """

    def __init__(self):

        self.embedding_service = (
            GeminiEmbeddingService()
        )

        self.vectorstore = ChromaStore()

        self.response_generator = (
            ResponseGenerator()
        )

        self.source_formatter = (
            SourceFormatter()
        )

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:

        query_embedding = (
            self.embedding_service.generate_query_embedding(
                question
            )
        )

        results = self.vectorstore.search(
            embedding=query_embedding,
            n_results=top_k,
        )

        documents = (
            results.get("documents", [[]])[0]
        )

        metadatas = (
            results.get("metadatas", [[]])[0]
        )

        if not documents:

            return {
                "success": False,
                "question": question,
                "answer": (
                    "Je n'ai trouvé aucun document pertinent."
                ),
                "sources": [],
                "chunks_used": 0,
            }

        answer = (
            self.response_generator.generate(
                question=question,
                contexts=documents,
            )
        )

        sources = (
            self.source_formatter.format(
                metadatas
            )
        )

        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": sources,
            "chunks_used": len(documents),
        }
