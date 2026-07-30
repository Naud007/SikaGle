from app.knowledge_engine.retrieval.keyword_retriever import (
    KeywordRetriever,
)
from app.knowledge_engine.retrieval.search_engine import (
    SearchEngine,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)
from app.knowledge_engine.retrieval.vector_retriever import (
    VectorRetriever,
)


class HybridRetriever:
    """
    Combine les recherches vectorielle et lexicale.
    """

    def __init__(self):

        self.vector = VectorRetriever()

        self.keyword = KeywordRetriever()

        self.engine = SearchEngine()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:

        vector_results = self.vector.search(
            query=query,
            top_k=top_k,
        )

        keyword_results = self.keyword.search(
            query=query,
            top_k=top_k,
        )

        return self.engine.merge(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k,
        )
