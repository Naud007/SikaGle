import time

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

        self.retriever = HybridRetriever()

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
        language: str = "fr",
        input_type: str = "text",
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
                "answer": (
                    "Je n'ai trouvé aucun "
                    "document pertinent."
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

        total_context_chars = sum(
            len(c) for c in contexts
        )

        print(
            "⏱️ [TIMING] Nombre de passages envoyés à Gemini : "
            f"{len(contexts)} "
            "| Taille totale du contexte : "
            f"{total_context_chars} caractères"
        )

        # =====================================================
        # DEBUG : TITRES ET SOURCE DES PASSAGES ENVOYÉS
        #
        # NOTE (diagnostic) :
        #
        # Ajouté pour comprendre pourquoi Gemini répond parfois
        # "information non disponible" alors que du contexte
        # est bien envoyé. On affiche ici, pour chaque passage,
        # son titre, sa source de récupération (vector/keyword)
        # et les 100 premiers caractères de son contenu.
        # =====================================================

        for index, (result, metadata) in enumerate(
            zip(results, metadatas),
            start=1,
        ):

            print(
                f"🔍 [DEBUG] Passage {index} | "
                f"source={getattr(result, 'source', '?')} | "
                f"titre={metadata.get('title', '?')} | "
                f"extrait={result.document[:100]!r}"
            )

        start_generation = time.time()

        answer = self.response_generator.generate(
            question=question,
            contexts=contexts,
            language=language,
            input_type=input_type,
        )

        print(
            "⏱️ [TIMING] Génération Gemini : "
            f"{time.time() - start_generation:.2f}s"
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