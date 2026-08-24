from datetime import datetime
import re
import unicodedata

from app.knowledge_engine.retrieval.search_query import (
    SearchQuery,
)
from app.knowledge_engine.retrieval.search_result import (
    SearchResult,
)


class SearchEngine:
    """
    Moteur de recherche documentaire hybride.

    Responsabilités :
        - fusion des résultats vectoriels et lexicaux
        - suppression des doublons
        - application des filtres
        - analyse de pertinence agricole
        - re-ranking
        - classement final

    Principe important :
        lorsqu'un concept agricole explicite est demandé,
        la pertinence de ce concept doit dominer la récence
        et les faibles ressemblances vectorielles.
    """

    # =========================================================
    # CONCEPTS AGRICOLES
    # =========================================================

    AGRICULTURAL_CONCEPTS = {
        "piment": [
            "piment",
            "piments",
            "pepper",
            "peppers",
            "sweet pepper",
            "chilli",
            "chili",
            "capsicum",
            "capsicum annuum",
            "capsicum spp",
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
            "pulgão",
            "pulgões",
        ],
        "ravageur": [
            "ravageur",
            "ravageurs",
            "pest",
            "pests",
            "insect pest",
            "insect pests",
        ],
        "insecte": [
            "insecte",
            "insectes",
            "insect",
            "insects",
        ],
    }

    # =========================================================
    # MOTS GÉNÉRIQUES
    # =========================================================

    STOPWORDS = {
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
        "par",
        "contre",
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
        "traitement",
        "traiter",
        "utiliser",
        "utilisation",
        "donner",
        "peut",
    }

    # =========================================================
    # TERMES LIÉS À LA LUTTE AGRICOLE
    # =========================================================

    MANAGEMENT_TERMS = {
        "traitement",
        "traiter",
        "lutte",
        "control",
        "controle",
        "contrôle",
        "management",
        "gestion",
        "insecticide",
        "insecticides",
        "biological control",
        "integrated pest management",
        "integrated pest",
        "pesticide",
        "pesticides",
        "extract",
        "extracts",
        "essential oil",
        "essential oils",
        "botanical",
        "natural enemies",
        "biological",
    }

    # =========================================================
    # FUSION
    # =========================================================

    def merge(
        self,
        vector_results: list[SearchResult],
        keyword_results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        merged: dict[str, SearchResult] = {}

        for result in vector_results:
            key = self._key(result)
            merged[key] = result

        for result in keyword_results:
            key = self._key(result)

            if key in merged:
                merged[key].keyword_score = result.keyword_score
            else:
                merged[key] = result

        results = list(merged.values())

        results = self.apply_filters(
            results,
            query,
        )

        results = self.rerank(
            results,
            query,
        )

        results.sort(
            key=lambda r: r.score,
            reverse=True,
        )

        return results[:query.top_k]

    # =========================================================
    # FILTRES
    # =========================================================

    def apply_filters(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        filtered = []

        for result in results:

            metadata = result.metadata or {}

            # -------------------------------------------------
            # SOURCE
            # -------------------------------------------------

            if query.source:

                source = str(
                    metadata.get(
                        "source",
                        "",
                    )
                )

                if source.lower() != query.source.lower():
                    continue

            # -------------------------------------------------
            # LANGUE
            # -------------------------------------------------

            if query.language:

                language = metadata.get("language")

                if language:
                    if (
                        str(language).lower()
                        != query.language.lower()
                    ):
                        continue

            # -------------------------------------------------
            # TYPE DOCUMENT
            # -------------------------------------------------

            if query.publication_type:

                publication_type = str(
                    metadata.get(
                        "publication_type",
                        metadata.get(
                            "document_type",
                            "",
                        ),
                    )
                )

                if (
                    publication_type.lower()
                    != query.publication_type.lower()
                ):
                    continue

            # -------------------------------------------------
            # ANNÉE
            # -------------------------------------------------

            if query.publication_year is not None:

                try:

                    year_value = metadata.get(
                        "publication_year"
                    )

                    if year_value is None:
                        year_value = metadata.get(
                            "published_at"
                        )

                    year = int(
                        str(year_value)[:4]
                    )

                except Exception:
                    continue

                if year != query.publication_year:
                    continue

            filtered.append(result)

        return filtered

    # =========================================================
    # RE-RANKING
    # =========================================================

    def rerank(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:

        for result in results:

            result.score = self.compute_score(
                result,
                query,
            )

        return results

    # =========================================================
    # SCORE FINAL
    # =========================================================

    def compute_score(
        self,
        result: SearchResult,
        query: SearchQuery,
    ) -> float:

        metadata = result.metadata or {}

        question = self._normalize(
            query.question
        )

        title = self._normalize(
            metadata.get("title", "")
        )

        crop = self._normalize(
            metadata.get("crop", "")
        )

        culture = self._normalize(
            metadata.get("culture", "")
        )

        keywords = self._normalize(
            metadata.get("keywords", "")
        )

        document = self._normalize(
            result.document or ""
        )

        # =====================================================
        # SCORE DE BASE
        # =====================================================

        score = 0.0

        score += result.vector_score * 10
        score += result.keyword_score * 0.75

        # =====================================================
        # MOTS IMPORTANTS
        # =====================================================

        important_words = self._extract_important_words(
            question
        )

        # =====================================================
        # MATCH TITRE
        # =====================================================

        title_matches = sum(
            1
            for word in important_words
            if self._contains_term(title, word)
        )

        score += min(
            title_matches * 1.5,
            4.5,
        )

        # =====================================================
        # MATCH MOTS-CLÉS
        # =====================================================

        keyword_matches = sum(
            1
            for word in important_words
            if self._contains_term(keywords, word)
        )

        score += min(
            keyword_matches * 1.0,
            3.0,
        )

        # =====================================================
        # MATCH CONTENU
        # =====================================================

        content_matches = sum(
            1
            for word in important_words
            if self._contains_term(document, word)
        )

        score += min(
            content_matches * 0.15,
            1.5,
        )

        # =====================================================
        # CONCEPTS AGRICOLES DEMANDÉS
        # =====================================================

        agricultural_matches = {}
        agricultural_score = 0.0

        for concept in self.AGRICULTURAL_CONCEPTS:

            if not self._question_contains_concept(
                question,
                concept,
            ):
                continue

            match = self._concept_match(
                concept=concept,
                crop=crop,
                culture=culture,
                title=title,
                keywords=keywords,
                document=document,
            )

            agricultural_matches[concept] = match
            agricultural_score += match["score"]

        score += agricultural_score

        # =====================================================
        # NOUVELLE RÈGLE :
        # TOUS LES CONCEPTS DEMANDÉS DOIVENT ÊTRE PRÉSENTS
        # =====================================================

        requested_concepts = list(
            agricultural_matches.keys()
        )

        missing_concepts = []

        for concept in requested_concepts:

            match = agricultural_matches[concept]

            has_match = any(
                [
                    match["crop"],
                    match["culture"],
                    match["title"],
                    match["keywords"],
                    match["document"],
                ]
            )

            if not has_match:
                missing_concepts.append(concept)

        # -----------------------------------------------------
        # Si un seul concept manque :
        # forte pénalité.
        # -----------------------------------------------------

        if missing_concepts:

            score -= 12.0 * len(
                missing_concepts
            )

        # -----------------------------------------------------
        # Si plusieurs concepts sont demandés
        # et qu'aucun n'est présent :
        # le document ne doit pas dominer.
        # -----------------------------------------------------

        if requested_concepts:

            all_missing = (
                len(missing_concepts)
                == len(requested_concepts)
            )

            if all_missing:

                score = min(
                    score,
                    -2.0,
                )

        # =====================================================
        # INTENTION AGRICOLE
        # =====================================================

        management_bonus = 0.0

        if self._contains_any_term(
            question,
            self.MANAGEMENT_TERMS,
        ):

            management_text = (
                f"{title} "
                f"{keywords} "
                f"{document}"
            )

            management_matches = sum(
                1
                for term in self.MANAGEMENT_TERMS
                if self._contains_term(
                    management_text,
                    self._normalize(term),
                )
            )

            management_bonus = min(
                management_matches * 0.25,
                0.75,
            )

            score += management_bonus

        # =====================================================
        # LANGUE
        # =====================================================

        language = self._normalize(
            metadata.get(
                "language",
                "",
            )
        )

        language_bonus = 0.0

        if language == "fr":

            language_bonus = 1.0
            score += language_bonus

        # =====================================================
        # RÉCENCE
        # =====================================================

        recency_bonus = 0.0

        try:

            publication_year = metadata.get(
                "publication_year"
            )

            if publication_year is None:

                published_at = metadata.get(
                    "published_at"
                )

                if published_at:
                    publication_year = str(
                        published_at
                    )[:4]

            year = int(
                str(publication_year)[:4]
            )

            current_year = datetime.now().year
            age = current_year - year

            if age <= 2:
                recency_bonus = 1.0

            elif age <= 5:
                recency_bonus = 0.5

            elif age <= 10:
                recency_bonus = 0.25

            score += recency_bonus

        except Exception:
            pass

        # =====================================================
        # DEBUG
        # =====================================================

        result.ranking_details = {

            "vector_score":
                result.vector_score,

            "keyword_score":
                result.keyword_score,

            "title_matches":
                title_matches,

            "keyword_matches":
                keyword_matches,

            "content_matches":
                content_matches,

            "agricultural_matches":
                agricultural_matches,

            "agricultural_score":
                agricultural_score,

            "missing_concepts":
                missing_concepts,

            "management_bonus":
                management_bonus,

            "language_bonus":
                language_bonus,

            "recency_bonus":
                recency_bonus,

            "final_score":
                score,
        }

        return score

    # =========================================================
    # MATCH AGRICOLE
    # =========================================================

    def _concept_match(
        self,
        concept: str,
        crop: str,
        culture: str,
        title: str,
        keywords: str,
        document: str,
    ) -> dict:

        aliases = [
            self._normalize(alias)
            for alias in self.AGRICULTURAL_CONCEPTS.get(
                concept,
                [],
            )
        ]

        crop_match = self._contains_any_alias(
            crop,
            aliases,
        )

        culture_match = self._contains_any_alias(
            culture,
            aliases,
        )

        title_match = self._contains_any_alias(
            title,
            aliases,
        )

        keyword_match = self._contains_any_alias(
            keywords,
            aliases,
        )

        document_match = self._contains_any_alias(
            document,
            aliases,
        )

        concept_score = 0.0

        # -----------------------------------------------------
        # CROP / CULTURE
        # -----------------------------------------------------

        if crop_match:
            concept_score += 5.0

        elif culture_match:
            concept_score += 4.5

        # -----------------------------------------------------
        # TITRE
        # -----------------------------------------------------

        if title_match:
            concept_score += 3.5

        # -----------------------------------------------------
        # MOTS-CLÉS
        # -----------------------------------------------------

        if keyword_match:
            concept_score += 2.5

        # -----------------------------------------------------
        # CONTENU
        # -----------------------------------------------------

        if document_match:
            concept_score += 0.5

        # -----------------------------------------------------
        # ABSENCE
        # -----------------------------------------------------

        if not (
            crop_match
            or culture_match
            or title_match
            or keyword_match
            or document_match
        ):

            concept_score -= 0.5

        return {
            "crop": crop_match,
            "culture": culture_match,
            "title": title_match,
            "keywords": keyword_match,
            "document": document_match,
            "score": concept_score,
        }

    # =========================================================
    # EXTRACTION DES MOTS IMPORTANTS
    # =========================================================

    def _extract_important_words(
        self,
        question: str,
    ) -> list[str]:

        words = []

        for raw_word in question.split():

            word = raw_word.strip(
                ".,;:!?()[]{}'\""
            )

            word = self._normalize(word)

            if len(word) < 4:
                continue

            if word in self.STOPWORDS:
                continue

            words.append(word)

        return list(
            dict.fromkeys(words)
        )

    # =========================================================
    # QUESTION → CONCEPT
    # =========================================================

    def _question_contains_concept(
        self,
        question: str,
        concept: str,
    ) -> bool:

        aliases = self.AGRICULTURAL_CONCEPTS.get(
            concept,
            [],
        )

        return self._contains_any_alias(
            question,
            [
                self._normalize(alias)
                for alias in aliases
            ],
        )

    # =========================================================
    # NORMALISATION
    # =========================================================

    @staticmethod
    def _normalize(value) -> str:

        text = str(
            value or ""
        ).lower()

        text = unicodedata.normalize(
            "NFKD",
            text,
        )

        text = "".join(
            char
            for char in text
            if not unicodedata.combining(char)
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # =========================================================
    # RECHERCHE D'UN TERME
    # =========================================================

    @staticmethod
    def _contains_term(
        text: str,
        term: str,
    ) -> bool:

        if not text or not term:
            return False

        if " " in term:
            return term in text

        return bool(
            re.search(
                rf"\b{re.escape(term)}\b",
                text,
            )
        )

    # =========================================================
    # RECHERCHE D'UN ALIAS
    # =========================================================

    def _contains_any_alias(
        self,
        text: str,
        aliases: list[str],
    ) -> bool:

        normalized_text = self._normalize(text)

        for alias in aliases:

            normalized_alias = self._normalize(
                alias
            )

            if not normalized_alias:
                continue

            # Correspondance normale
            if self._contains_term(
                normalized_text,
                normalized_alias,
            ):
                return True

            # Correspondance par préfixe pour les
            # variantes lexicales agricoles :
            # aphid -> aphids
            # puceron -> pucerons
            # pulgao -> pulgoes, etc.
            if " " not in normalized_alias:
                pattern = (
                    rf"\b{re.escape(normalized_alias)}"
                    rf"(?:s|es)?\b"
                )

                if re.search(
                    pattern,
                    normalized_text,
                ):
                    return True

        return False

    # =========================================================
    # RECHERCHE D'UN TERME PARMI UNE LISTE
    # =========================================================

    def _contains_any_term(
        self,
        text: str,
        terms,
    ) -> bool:

        normalized_text = self._normalize(
            text
        )

        for term in terms:

            normalized_term = self._normalize(
                term
            )

            if self._contains_term(
                normalized_text,
                normalized_term,
            ):
                return True

        return False

    # =========================================================
    # CLÉ UNIQUE D'UN CHUNK
    # =========================================================

    @staticmethod
    def _key(
        result: SearchResult,
    ) -> str:

        metadata = result.metadata or {}

        document_id = (
            metadata.get("document")
            or metadata.get("document_id")
            or metadata.get("identifier")
            or result.document[:80]
        )

        chunk_index = metadata.get(
            "chunk_index"
        )

        if chunk_index is not None:

            return (
                f"{document_id}"
                f"::chunk::{chunk_index}"
            )

        return str(document_id)