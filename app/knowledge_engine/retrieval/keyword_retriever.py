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
            "piments",
            "pepper",
            "peppers",
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
            "aphididae",
            "pulgão",
            "pulgões",
            "pulgon",
            "pulgones",
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
        self.repository = KnowledgeRepository()

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

        # -------------------------------------------------
        # Récupération paginée de tous les documents
        # -------------------------------------------------

        rows = []

        page_size = 1000
        offset = 0

        while True:
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
                .range(
                    offset,
                    offset + page_size - 1,
                )
                .execute()
            )

            batch = response.data or []

            if not batch:
                break

            rows.extend(batch)

            if len(batch) < page_size:
                break

            offset += page_size

        # -------------------------------------------------
        # Calcul des résultats
        # -------------------------------------------------

        results: list[SearchResult] = []

        for row in rows:

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
                query.question,
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

        return results[:query.top_k]

    def _extract_keywords(
        self,
        question: str,
    ) -> list[str]:
        """
        Extrait les mots importants de la question
        et ajoute automatiquement les synonymes
        correspondant aux concepts connus.
        """

        words = [
            word.lower().strip(
                ".,;:!?()[]{}'\""
            )
            for word in question.split()
            if len(word) >= 3
        ]

        keywords = []

        for word in words:

            keywords.append(word)

            # Forme singulière simple
            if word.endswith("s"):
                keywords.append(
                    word[:-1]
                )

            # -------------------------------------------------
            # Trouver le concept auquel appartient le mot
            # -------------------------------------------------

            matched_concept = None

            for concept, aliases in self.SYNONYMS.items():

                normalized_aliases = [
                    alias.lower()
                    for alias in aliases
                ]

                if (
                    word == concept
                    or word in normalized_aliases
                    or (
                        word.endswith("s")
                        and word[:-1]
                        in normalized_aliases
                    )
                ):
                    matched_concept = concept
                    break

            # -------------------------------------------------
            # Ajouter tous les synonymes du concept
            # -------------------------------------------------

            if matched_concept:

                keywords.append(
                    matched_concept
                )

                keywords.extend(
                    self.SYNONYMS[
                        matched_concept
                    ]
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
        question: str,
    ) -> int:
        """
        Calcule un score lexical pondéré.

        Les mots génériques sont ignorés.
        Les correspondances utilisent des mots entiers
        afin d'éviter les faux positifs par sous-chaînes.
        """

        import re

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

            if " " in keyword:

                count = lower.count(
                    keyword
                )

            else:

                count = len(
                    re.findall(
                        rf"\b{re.escape(keyword)}\b",
                        lower,
                    )
                )

            if count > 0:

                score += min(
                    count,
                    3,
                )

        return score