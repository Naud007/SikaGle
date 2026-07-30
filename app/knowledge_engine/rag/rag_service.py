from app.knowledge_engine.rag.response_generator import (
    ResponseGenerator,
)
from app.knowledge_engine.rag.source_formatter import (
    SourceFormatter,
)
from app.knowledge_engine.retrieval import (
    HybridRetriever,
    SearchQuery,
)


class RAGService:

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
        source: str | None = None,
        language: str | None = None,
        publication_type: str | None = None,
        publication_year: int | None = None,
    ) -> dict:

        search_query = SearchQuery(

            question=question,

            top_k=top_k,

            source=source,

            language=language,

            publication_type=publication_type,

            publication_year=publication_year,
        )

        results = self.retriever.search(
            search_query
        )

        if not results:

            return {

                "success": False,

                "question": question,

                "answer": "Je n'ai trouvé aucun document pertinent.",

                "sources": [],

                "chunks_used": 0,
            }

        contexts = [
            r.document
            for r in results
        ]

        metadatas = [
            r.metadata
            for r in results
        ]

        answer = self.response_generator.generate(
            question=question,
            contexts=contexts,
        )

        sources = self.source_formatter.format(
            metadatas
        )

        return {

            "success": True,

            "question": question,

            "answer": answer,

            "sources": sources,

            "chunks_used": len(contexts),
        }
