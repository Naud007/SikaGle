from app.knowledge_engine.repositories import (
    KnowledgeRepository,
)
from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class KeywordRetriever:
    """
    Recherche lexicale dans les documents stockés
    dans Supabase.

    La recherche utilise :
        - les mots de la question
        - quelques équivalences agricoles multilingues
        - le titre
        - le contenu
        - les mots-clés
    """

    SYNONYMS = {
        "piment": [
            "piment",
            "pepper",
            "chilli",
            "chili",
            "capsicum",
        ],
        "puceron": [
            "puceron",
            "pucerons",
            "aphid",
            "aphids",
            "aphis",
        ],
        "ravageur": [
            "ravageur",
            "ravageurs",
            "pest",
            "pests",
        ],
        "insecte": [
            "insecte",
            "insectes",
            "insect",
            "insects",
        ],
    }

    def __init__(self):

        self.repository = (
            KnowledgeRepository()
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        """
        Recherche les documents contenant les mots
        ou équivalents importants de la question.
        """

        keywords = self._extract_keywords(
            query.question
        )

        if not keywords:
            return []

        response = (
            self.repository.vectorstore.client
            .table(
                self.repository.vectorstore.TABLE_NAME
            )
            .select(
                "document_id, chunk_index, chunk_count, "
                "title, source, identifier, url, author, "
                "published_at, language, document_type, "
                "publisher, crop, culture, keywords, "
                "country, zone_geographique, content"
            )
            .limit(1000)
            .execute()
        )

        results: list[SearchResult] = []

        for row in response.data or []:

            content = str(
                row.get("content") or ""
            )

            title = str(
                row.get("title") or ""
            )

            keywords_metadata = str(
                row.get("keywords") or ""
            )

            searchable_text = (
                f"{title} "
                f"{content} "
                f"{keywords_metadata}"
            )

            score = self._keyword_score(
                searchable_text,
                keywords,
            )

            if score <= 0:
                continue

            metadata = {
                "document": row.get(
                    "document_id"
                ),
                "chunk_index": row.get(
                    "chunk_index"
                ),
                "chunk_count": row.get(
                    "chunk_count"
                ),
                "title": row.get(
                    "title"
                ),
                "source": row.get(
                    "source"
                ),
                "identifier": row.get(
                    "identifier"
                ),
                "url": row.get(
                    "url"
                ),
                "author": row.get(
                    "author"
                ),
                "published_at": row.get(
                    "published_at"
                ),
                "language": row.get(
                    "language"
                ),
                "document_type": row.get(
                    "document_type"
                ),
                "publisher": row.get(
                    "publisher"
                ),
                "crop": row.get(
                    "crop"
                ),
                "culture": row.get(
                    "culture"
                ),
                "keywords": row.get(
                    "keywords"
                ),
                "country": row.get(
                    "country"
                ),
                "zone_geographique": row.get(
                    "zone_geographique"
                ),
            }

            metadata = {
                key: value
                for key, value in metadata.items()
                if value is not None
            }

            results.append(
                SearchResult(
                    document=content,
                    metadata=metadata,
                    keyword_score=float(score),
                    score=float(score),
                    source="keyword",
                )
            )

        results.sort(
            key=lambda result: result.keyword_score,
            reverse=True,
        )

        return results[
            :query.top_k
        ]

    def _extract_keywords(
        self,
        question: str,
    ) -> list[str]:
        """
        Extrait les mots importants et leurs
        équivalents documentaires.
        """

        words = [
            word.lower().strip(
                ".,;:!?()[]{}"
            )
            for word in question.split()
            if len(word) >= 3
        ]

        keywords = []

        for word in words:

            keywords.append(word)

            if word.endswith("s"):
                keywords.append(
                    word[:-1]
                )

            synonyms = self.SYNONYMS.get(
                word
            )

            if synonyms:
                keywords.extend(
                    synonyms
                )

        return list(
            dict.fromkeys(
                keywords
            )
        )

    def _keyword_score(
        self,
        text: str,
        keywords: list[str],
    ) -> int:
        """
        Calcule un score lexical pondéré.

        Les mots génériques sont ignorés afin
        d'éviter qu'ils dominent les résultats.
        """

        lower = text.lower()

        stopwords = {
            "quel",
            "quelle",
            "quels",
            "quelles",
            "est",
            "sont",
            "les",
            "des",
            "du",
            "de",
            "la",
            "le",
            "un",
            "une",
            "et",
            "ou",
            "sur",
            "dans",
            "avec",
            "pour",
            "comment",
            "reconnaître",
            "reconnaitre",
            "faire",
            "avoir",
            "mon",
            "ma",
            "mes",
            "son",
            "sa",
            "ses",
        }

        score = 0

        for keyword in keywords:

            keyword = keyword.lower().strip()

            if not keyword:
                continue

            if keyword in stopwords:
                continue

            if len(keyword) < 4:
                continue

            count = lower.count(
                keyword
            )

            if count > 0:

                # Limiter l'effet des répétitions
                # dans un même document.
                score += min(
                    count,
                    3,
                )

        return score