from app.knowledge_engine.retrieval.keyword_retriever import KeywordRetriever
from app.knowledge_engine.retrieval.search_query import SearchQuery

import os

from supabase import create_client, Client

from app.ai.embeddings import (
    GeminiEmbeddingService
)

from app.ai.gemini_client import (
    GeminiClient
)


# =========================================================
# SERVICE RAG SIKAGLÉ
# =========================================================

class RAGService:

    def __init__(self):

        # =====================================================
        # CONFIGURATION SUPABASE
        # =====================================================

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url:
            raise ValueError(
                "SUPABASE_URL est manquante."
            )

        if not supabase_key:
            raise ValueError(
                "SUPABASE_KEY est manquante."
            )

        # =====================================================
        # CONNEXION SUPABASE
        # =====================================================

        self.supabase: Client = create_client(
            supabase_url,
            supabase_key
        )

        print(
            "[RAG] Connexion Supabase initialisée."
        )

        # =====================================================
        # SERVICE EMBEDDING
        # =====================================================

        self.embedding_service = (
            GeminiEmbeddingService(
                model="jina-embeddings-v3",
                output_dimensionality=1024
            )
        )

        # =====================================================
        # CLIENT GEMINI
        # =====================================================

        self.gemini = GeminiClient()

        # =====================================================
        # RETRIEVER KEYWORD
        # =====================================================

        self.keyword_retriever = KeywordRetriever()

    # =========================================================
    # ENRICHIR LA REQUÊTE AGRICOLE
    # =========================================================

    def enrich_query(
        self,
        query: str
    ) -> str:

        query_lower = query.lower()

        agricultural_terms = []

        # =====================================================
        # CULTURE : PIMENT
        # =====================================================

        if any(
            term in query_lower
            for term in [
                "piment",
                "poivron",
                "capsicum"
            ]
        ):

            agricultural_terms.extend([
                "Capsicum annuum",
                "pepper",
                "chilli"
            ])

        # =====================================================
        # PUCERONS
        # =====================================================

        if any(
            term in query_lower
            for term in [
                "puceron",
                "pucerons",
                "aphid",
                "aphids",
                "aphis"
            ]
        ):

            agricultural_terms.extend([
                "aphid",
                "Aphis",
                "Aphididae",
                "puceron"
            ])

        # =====================================================
        # JAUNISSEMENT
        # =====================================================

        if any(
            term in query_lower
            for term in [
                "jaun",
                "jaunissement",
                "jaunes",
                "jaune"
            ]
        ):

            agricultural_terms.extend([
                "yellowing leaves",
                "leaf yellowing",
                "chlorosis"
            ])

        # =====================================================
        # MALADIE / FEUILLES
        # =====================================================

        if any(
            term in query_lower
            for term in [
                "jaun",
                "maladie",
                "feuille",
                "feuilles"
            ]
        ):

            agricultural_terms.extend([
                "nutrient deficiency",
                "nitrogen",
                "iron",
                "magnesium",
                "potassium",
                "phosphorus",
                "disease",
                "pest"
            ])

        # =====================================================
        # AUCUN ENRICHISSEMENT
        # =====================================================

        if not agricultural_terms:
            return query

        # =====================================================
        # SUPPRESSION DES DOUBLONS
        # =====================================================

        agricultural_terms = list(
            dict.fromkeys(
                agricultural_terms
            )
        )

        enriched_query = (
            f"{query} "
            + " ".join(agricultural_terms)
        )

        print(
            "[RAG] Requête enrichie :",
            enriched_query
        )

        return enriched_query

    # =========================================================
    # RECHERCHE VECTORIELLE
    # =========================================================

    def search_vector_documents(
        self,
        query: str,
        match_threshold: float = 0.20,
        match_count: int = 10
    ):

        if not query or not query.strip():
            raise ValueError(
                "La question de recherche est vide."
            )

        query = query.strip()

        search_query = self.enrich_query(
            query
        )

        print("=" * 60)
        print("[RAG] Question :", query)
        print("[RAG] Recherche vectorielle :", search_query)
        print("=" * 60)

        # =====================================================
        # EMBEDDING
        # =====================================================

        print(
            "[RAG] Génération embedding de la question..."
        )

        query_embedding = (
            self.embedding_service
            .generate_query_embedding(
                search_query
            )
        )

        if not query_embedding:
            raise RuntimeError(
                "Impossible de générer l'embedding de la question."
            )

        print(
            "[RAG] Embedding généré :",
            len(query_embedding),
            "dimensions"
        )

        # =====================================================
        # RECHERCHE SUPABASE
        # =====================================================

        print(
            "[RAG] Recherche vectorielle dans Supabase..."
        )

        response = (
            self.supabase
            .rpc(
                "match_knowledge_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count
                }
            )
            .execute()
        )

        documents = response.data or []

        print(
            "[RAG] Documents vectoriels trouvés :",
            len(documents)
        )

        for index, document in enumerate(
            documents,
            start=1
        ):

            print(
                f"[RAG] Vectoriel {index} :",
                document.get("title")
            )

            print(
                "[RAG] Similarité :",
                document.get("similarity")
            )

        return documents

    # =========================================================
    # RECHERCHE KEYWORD
    # =========================================================

    def search_keyword_documents(
        self,
        query: str,
        top_k: int = 10
    ):

        print("=" * 60)
        print("[RAG] Recherche keyword :", query)
        print("=" * 60)

        try:

            search_query = SearchQuery(
                question=query,
                top_k=top_k,
                language="fr"
            )

            documents = self.keyword_retriever.search(
                search_query
            )

            print(
                "[RAG] Documents keyword trouvés :",
                len(documents)
            )

            for index, document in enumerate(
                documents,
                start=1
            ):

                print(
                    f"[RAG] Keyword {index} :",
                    document.metadata.get("title")
                )

                print(
                    "[RAG] Keyword score :",
                    document.keyword_score
                )

            return documents

        except Exception as e:

            print(
                "[RAG] Erreur recherche keyword :",
                e
            )

            return []

    # =========================================================
    # CONVERSION DOCUMENT KEYWORD → DOCUMENT RAG
    # =========================================================

    def keyword_to_document(
        self,
        keyword_document
    ):

        metadata = (
            keyword_document.metadata
            or {}
        )

        return {
            "id": metadata.get("id"),
            "title": metadata.get("title"),
            "source": metadata.get("source"),
            "url": metadata.get("url"),
            "content": (
                metadata.get("content")
                or getattr(
                    keyword_document,
                    "content",
                    ""
                )
            ),
            "similarity": None,
            "keyword_score": getattr(
                keyword_document,
                "keyword_score",
                0
            )
        }

    # =========================================================
    # FUSION VECTORIEL + KEYWORD
    # =========================================================

    def merge_documents(
        self,
        vector_documents,
        keyword_documents,
        match_count=5
    ):

        merged = []
        seen_ids = set()

        # =====================================================
        # 1. DOCUMENTS KEYWORD PERTINENTS
        # =====================================================

        for document in keyword_documents:

            converted = self.keyword_to_document(
                document
            )

            document_id = converted.get("id")

            if document_id is not None:

                if document_id in seen_ids:
                    continue

                seen_ids.add(
                    document_id
                )

            merged.append(
                converted
            )

        # =====================================================
        # 2. DOCUMENTS VECTORIELS
        # =====================================================

        for document in vector_documents:

            document_id = document.get("id")

            if document_id is not None:

                if document_id in seen_ids:
                    continue

                seen_ids.add(
                    document_id
                )

            merged.append(
                document
            )

        # =====================================================
        # LIMITATION
        # =====================================================

        return merged[:match_count]

    # =========================================================
    # RECHERCHE DOCUMENTAIRE COMPLÈTE
    # =========================================================

    def search_documents(
        self,
        query: str,
        match_threshold: float = 0.20,
        match_count: int = 5
    ):

        if not query or not query.strip():
            raise ValueError(
                "La question de recherche est vide."
            )

        query = query.strip()

        # =====================================================
        # RECHERCHE VECTORIELLE
        # =====================================================

        vector_documents = (
            self.search_vector_documents(
                query=query,
                match_threshold=match_threshold,
                match_count=match_count
            )
        )

        # =====================================================
        # DÉTECTION QUESTION RAVAGEUR
        # =====================================================

        query_lower = query.lower()

        pest_question = any(
            term in query_lower
            for term in [
                "puceron",
                "pucerons",
                "aphid",
                "aphids",
                "aphis",
                "ravageur",
                "insecte",
                "insectes"
            ]
        )

        # =====================================================
        # RECHERCHE KEYWORD SI QUESTION SPÉCIFIQUE
        # =====================================================

        keyword_documents = []

        if pest_question:

            print(
                "[RAG] Question ravageur détectée."
            )

            keyword_documents = (
                self.search_keyword_documents(
                    query=query,
                    top_k=max(
                        match_count,
                        10
                    )
                )
            )

        # =====================================================
        # SI KEYWORD DISPONIBLE :
        # PRIORITÉ AUX DOCUMENTS KEYWORD
        # =====================================================

        if keyword_documents:

            documents = self.merge_documents(
                vector_documents=vector_documents,
                keyword_documents=keyword_documents,
                match_count=match_count
            )

        else:

            documents = vector_documents[:match_count]

        print(
            "[RAG] Documents finaux :",
            len(documents)
        )

        for index, document in enumerate(
            documents,
            start=1
        ):

            print(
                f"[RAG] Document final {index} :",
                document.get("title")
            )

        return documents

    # =========================================================
    # CONSTRUIRE LE CONTEXTE POUR GEMINI
    # =========================================================

    def build_context(
        self,
        documents
    ):

        context_parts = []

        for index, document in enumerate(
            documents,
            start=1
        ):

            title = (
                document.get("title")
                or "Document sans titre"
            )

            source = (
                document.get("source")
                or "Source inconnue"
            )

            url = (
                document.get("url")
                or ""
            )

            content = (
                document.get("content")
                or ""
            )

            content = content[:6000]

            part = (
                f"DOCUMENT {index}\n"
                f"Titre : {title}\n"
                f"Source : {source}\n"
                f"URL : {url}\n\n"
                f"{content}"
            )

            context_parts.append(
                part
            )

        return (
            "\n\n"
            "========================================\n\n"
            .join(context_parts)
        )

    # =========================================================
    # FILTRE DE SÉCURITÉ PHYTOSANITAIRE
    # =========================================================

    def sanitize_answer(
        self,
        answer: str
    ):

        if not answer:
            return answer

        forbidden_terms = [
            "imidaclopride",
            "imidacloprid",
            "glyphosate",
            "paraquat",
            "chlorpyrifos",
            "cyperméthrine",
            "cypermethrin",
            "lambda-cyhalothrine",
            "lambda-cyhalothrin",
            "acétamipride",
            "acetamiprid",
            "thiaméthoxame",
            "thiamethoxam",
        ]

        lines = answer.splitlines()

        cleaned_lines = []

        for line in lines:

            line_lower = line.lower()

            if any(
                term in line_lower
                for term in forbidden_terms
            ):
                continue

            cleaned_lines.append(
                line
            )

        return "\n".join(
            cleaned_lines
        ).strip()

    # =========================================================
    # GÉNÉRER LA RÉPONSE
    # =========================================================

    def generate_answer(
        self,
        query: str,
        documents
    ):

        if not documents:

            return (
                "Je n'ai pas trouvé suffisamment "
                "d'informations fiables dans ma base "
                "documentaire pour répondre précisément "
                "à cette question."
            )

        context = self.build_context(
            documents
        )

        prompt = f"""
Tu es SikaGlé, un assistant agricole intelligent.

Ta mission est d'aider les agriculteurs avec des réponses
simples, pratiques, compréhensibles et fiables.

QUESTION DE L'UTILISATEUR :

{query}


INFORMATIONS DOCUMENTAIRES DISPONIBLES :

{context}


RÈGLES IMPORTANTES :

1. Réponds principalement à partir des documents fournis.

2. Si les documents ne permettent pas de répondre,
   dis-le clairement.

3. Ne présente jamais une information absente des documents
   comme venant des documents.

4. Ne transforme pas une étude étrangère en recommandation
   spécifique au Bénin.

5. Si les documents sont hors sujet ou insuffisants,
   reconnais-le.

6. Réponds en français simple et naturel.

7. Réponds directement à la question.

8. Fais une réponse courte et pratique.

9. Ne recopie pas les documents.

10. Évite le jargon scientifique inutile.

11. SÉCURITÉ PHYTOSANITAIRE :

    Ne recommande jamais de pesticide, insecticide,
    herbicide, fongicide ou autre produit phytosanitaire
    chimique.

    Ne donne jamais de dosage, concentration,
    fréquence d'application ou quantité précise.

    Si un document contient un traitement chimique,
    ignore cette partie.

12. PRIORITÉ AUX MÉTHODES À FAIBLE RISQUE :

    - surveillance ;
    - prévention ;
    - méthodes culturales ;
    - méthodes mécaniques ;
    - lutte biologique ;
    - solutions végétales ou biologiques,
      uniquement lorsqu'elles sont réellement
      soutenues par les documents.

13. Ne présente pas une méthode comme provenant
    des documents si elle n'y apparaît pas.

14. Si une information importante manque,
    pose une question courte.

15. La réponse doit être adaptée à WhatsApp.

16. Utilise quelques points seulement si nécessaire.

17. Ne mets pas de bibliographie dans la réponse.

18. Ton objectif est d'être immédiatement utile.

Réponds maintenant à la question.
"""

        print(
            "[RAG] Génération de la réponse avec Gemini..."
        )

        answer = self.gemini.generate_text(
            prompt
        )

        return self.sanitize_answer(
            answer
        )

    # =========================================================
    # QUESTION COMPLÈTE
    # =========================================================

    def answer(
        self,
        query: str,
        match_threshold: float = 0.20,
        match_count: int = 5
    ):

        documents = self.search_documents(
            query=query,
            match_threshold=match_threshold,
            match_count=match_count
        )

        answer = self.generate_answer(
            query=query,
            documents=documents
        )

        # =====================================================
        # SOURCES
        # =====================================================

        sources = []

        seen_sources = set()

        for document in documents:

            source_url = (
                document.get("url")
                or document.get("document_id")
            )

            if (
                source_url
                and source_url not in seen_sources
            ):

                seen_sources.add(
                    source_url
                )

                sources.append(
                    {
                        "title": document.get("title"),
                        "organization": document.get("source"),
                        "url": source_url,
                        "similarity": document.get("similarity")
                    }
                )

        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "documents_found": len(documents),
            "sources": sources
        }


# =========================================================
# TEST RAG
# =========================================================

def test_rag():

    try:

        rag = RAGService()

        question = (
            "Quel est l'effet de la matière organique "
            "et de la fertilisation sur la fertilité "
            "des sols ?"
        )

        result = rag.answer(
            query=question,
            match_threshold=0.20,
            match_count=5
        )

        return result

    except Exception as e:

        print(
            "[RAG] Erreur :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }