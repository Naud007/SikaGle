import time

from concurrent.futures import ThreadPoolExecutor

from app.knowledge_engine.retrieval.keyword_retriever import (
    KeywordRetriever,
)
from app.knowledge_engine.retrieval.search_engine import (
    SearchEngine,
)
from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)
from app.knowledge_engine.retrieval.vector_retriever import (
    VectorRetriever,
)


class HybridRetriever:

    def __init__(self):

        self.vector = VectorRetriever()

        self.keyword = KeywordRetriever()

        self.engine = SearchEngine()

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        # =====================================================
        # RECHERCHE VECTORIELLE + KEYWORD EN PARALLÈLE
        #
        # NOTE (correctif performance) :
        #
        # Ces deux recherches sont totalement indépendantes
        # (l'une passe par Jina + Supabase, l'autre uniquement
        # par Supabase). Elles étaient exécutées l'une après
        # l'autre, ce qui additionnait inutilement leurs temps.
        # On les lance maintenant en parallèle avec
        # ThreadPoolExecutor et on attend simplement la plus
        # lente des deux, sans changer aucun résultat.
        # =====================================================

        start_parallel = time.time()

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:

            vector_future = executor.submit(
                self.vector.search,
                query,
            )

            keyword_future = executor.submit(
                self.keyword.search,
                query,
            )

            vector_results = (
                vector_future.result()
            )

            keyword_results = (
                keyword_future.result()
            )

        print(
            "⏱️ [TIMING] Recherche vectorielle + keyword "
            "(en parallèle) : "
            f"{time.time() - start_parallel:.2f}s"
        )

        start_merge = time.time()

        results = self.engine.merge(
            vector_results=vector_results,
            keyword_results=keyword_results,
            query=query,
        )

        print(
            "⏱️ [TIMING] Merge : "
            f"{time.time() - start_merge:.2f}s"
        )

        return results