from app.knowledge_engine.retrieval.search_query import SearchQuery
from app.knowledge_engine.retrieval.search_result import SearchResult


class KeywordRetriever:
    """
    Recherche lexicale PostgreSQL pour SikaGlé.

    La recherche est exécutée côté Supabase afin d'éviter
    de récupérer toute la table knowledge_embeddings dans Python.
    """

    def __init__(self, repository=None):
        if repository is None:
            from app.knowledge_engine.repositories import KnowledgeRepository

            repository = KnowledgeRepository()

        self.repository = repository

    # =========================================================
    # EXTRACTION DES MOTS-CLÉS
    # =========================================================

    def _extract_keywords(self, question: str) -> list[str]:

        if not question:
            return []

        import re

        text = question.lower()

        # Suppression des accents simples
        replacements = {
            "à": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "î": "i",
            "ï": "i",
            "ô": "o",
            "ö": "o",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ÿ": "y",
            "ç": "c",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        words = re.findall(
            r"[a-zA-ZÀ-ÿ]+",
            text
        )

        return list(
            dict.fromkeys(words)
        )

    # =========================================================
    # RECHERCHE
    # =========================================================

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        keywords = self._extract_keywords(
            query.question
        )

        if not keywords:
            return []

        # =====================================================
        # MOTS VIDES
        # =====================================================

        stopwords = {
            "quel",
            "quelle",
            "quels",
            "quelles",
            "est",
            "sont",
            "avec",
            "pour",
            "comment",
            "faire",
            "avoir",
            "jai",
            "j",
            "des",
            "de",
            "du",
            "sur",
            "mes",
            "mon",
            "ma",
            "me",
            "moi",
            "que",
            "dois",
            "doit",
            "doivent",
            "les",
            "le",
            "la",
            "un",
            "une",
            "et",
            "ou",
            "dans",
            "ce",
            "ces",
            "cet",
            "cette",
            "plant",
            "plants",
        }

        search_terms = [
            keyword.strip()
            for keyword in keywords
            if keyword
            and len(keyword.strip()) >= 4
            and keyword.strip() not in stopwords
        ]

        if not search_terms:
            return []

        # =====================================================
        # TERMES AGRICOLES
        # =====================================================

        pest_terms = {
            "puceron",
            "pucerons",
            "aphid",
            "aphids",
            "aphis",
            "aphididae",
            "ravageur",
            "ravageurs",
            "insecte",
            "insectes",
        }

        crop_terms = {
            "piment",
            "piments",
            "pepper",
            "peppers",
            "chilli",
            "chili",
            "capsicum",
            "poivron",
            "poivrons",
        }

        # =====================================================
        # NORMALISATION
        # =====================================================

        normalized_terms = {
            term.lower().strip()
            for term in search_terms
        }

        has_pest = bool(
            normalized_terms.intersection(
                pest_terms
            )
        )

        has_crop = bool(
            normalized_terms.intersection(
                crop_terms
            )
        )

        # =====================================================
        # REQUÊTE CIBLÉE
        # =====================================================

        concept_query = []

        if has_pest:

            concept_query.append(
                "("
                "puceron OR pucerons OR "
                "aphid OR aphids OR aphis OR aphididae"
                ")"
            )

        if has_crop:

            concept_query.append(
                "("
                "piment OR piments OR "
                "pepper OR peppers OR "
                "chilli OR chili OR capsicum OR "
                "poivron OR poivrons"
                ")"
            )

        if len(concept_query) == 2:

            search_query = (
                f"{concept_query[0]} AND "
                f"{concept_query[1]}"
            )

        elif len(concept_query) == 1:

            search_query = concept_query[0]

        else:

            search_query = " OR ".join(
                dict.fromkeys(
                    search_terms
                )
            )

        print(
            "[KEYWORD] Requête PostgreSQL :",
            search_query
        )

        # =====================================================
        # SUPABASE
        # =====================================================

        response = (
            self.repository
            .vectorstore
            .client
            .rpc(
                "search_knowledge_keywords",
                {
                    "search_query": search_query,
                    "result_limit": max(
                        query.top_k,
                        20
                    ),
                },
            )
            .execute()
        )

        rows = response.data or []

        # =====================================================
        # RERANKING AGRICOLE
        # =====================================================

        reranked = []

        for row in rows:

            title = str(
                row.get("title") or ""
            ).lower()

            content = str(
                row.get("content") or ""
            ).lower()

            keywords_text = str(
                row.get("keywords") or ""
            ).lower()

            crop = str(
                row.get("crop") or ""
            ).lower()

            culture = str(
                row.get("culture") or ""
            ).lower()

            combined_text = (
                title
                + " "
                + content
                + " "
                + keywords_text
            )

            score = float(
                row.get("rank") or 0.0
            )

            # -------------------------------------------------
            # PRIORITÉ RAVAGEUR
            # -------------------------------------------------

            if has_pest:

                if any(
                    term in combined_text
                    for term in pest_terms
                ):
                    score += 2.0

            # -------------------------------------------------
            # PRIORITÉ CULTURE
            # -------------------------------------------------

            if has_crop:

                crop_match = any(
                    term in (
                        title
                        + " "
                        + crop
                        + " "
                        + culture
                    )
                    for term in crop_terms
                )

                if crop_match:
                    score += 4.0

                # Recherche également dans le contenu
                content_crop_match = any(
                    term in combined_text
                    for term in crop_terms
                )

                if content_crop_match:
                    score += 1.0

            # -------------------------------------------------
            # BONUS SI RAVAGEUR + CULTURE
            # -------------------------------------------------

            if has_pest and has_crop:

                pest_match = any(
                    term in combined_text
                    for term in pest_terms
                )

                crop_match = any(
                    term in combined_text
                    for term in crop_terms
                )

                if pest_match and crop_match:
                    score += 3.0

            reranked.append(
                (
                    score,
                    row
                )
            )

        # =====================================================
        # TRI
        # =====================================================

        reranked.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # =====================================================
        # CONVERSION → SearchResult
        # =====================================================

        results: list[SearchResult] = []

        for score, row in reranked:

            content = str(
                row.get("content") or ""
            )

            metadata = {
                "id": row.get("id"),
                "document": row.get("document_id"),
                "chunk_index": row.get("chunk_index"),
                "chunk_count": row.get("chunk_count"),
                "title": row.get("title"),
                "source": row.get("source"),
                "identifier": row.get("identifier"),
                "url": row.get("url"),
                "author": row.get("author"),
                "published_at": row.get("published_at"),
                "language": row.get("language"),
                "document_type": row.get("document_type"),
                "publisher": row.get("publisher"),
                "crop": row.get("crop"),
                "culture": row.get("culture"),
                "keywords": row.get("keywords"),
                "country": row.get("country"),
                "zone_geographique": row.get(
                    "zone_geographique"
                ),
                "content": content,
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
                    keyword_score=score,
                    score=score,
                    source="keyword",
                )
            )

        return results[:query.top_k]