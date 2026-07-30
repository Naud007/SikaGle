from app.knowledge_engine.rag.response_generator import (
    ResponseGenerator,
)
from app.knowledge_engine.rag.source_formatter import (
    SourceFormatter,
)
from app.knowledge_engine.retrieval import (
    HybridRetriever,
)


class RAGService:
    """
    Pipeline RAG complet.

        Question
            ↓
    HybridRetriever
            ↓
    Génération de réponse
            ↓
    Formatage des sources
    """

    def __init__(self):

        self.retriever = (
            HybridRetriever()
        )

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

        results = self.retriever.search(
            query=question,
            top_k=top_k,
        )

        if not results:

            return {

                "success": False,

                "question": question,

                "answer": (
                    "Je n'ai trouvé aucun document pertinent."
                ),

                "sources": [],

                "chunks_used": 0,
            }

        contexts = [

            result.document

            for result in results
        ]

        metadatas = [

            result.metadata

            for result in results
        ]

        answer = (
            self.response_generator.generate(

                question=question,

                contexts=contexts,
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

            "chunks_used": len(
                contexts
            ),
        }
