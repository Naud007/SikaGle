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

        vector_results = self.vector.search(
            query
        )

        keyword_results = self.keyword.search(
            query
        )

        return self.engine.merge(
            vector_results,
            keyword_results,
            top_k=query.top_k,
        )
