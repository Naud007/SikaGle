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

        supabase_url = os.getenv(
            "SUPABASE_URL"
        )

        supabase_key = os.getenv(
            "SUPABASE_KEY"
        )

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

        self.supabase: Client = (
            create_client(
                supabase_url,
                supabase_key
            )
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

        self.gemini = (
            GeminiClient()
        )


    # =========================================================
    # RECHERCHE VECTORIELLE
    # =========================================================

    def search_documents(
        self,
        query: str,
        match_threshold: float = 0.20,
        match_count: int = 5
    ):

        # =====================================================
        # VALIDATION
        # =====================================================

        if not query or not query.strip():

            raise ValueError(
                "La question de recherche est vide."
            )

        query = query.strip()

        print("=" * 60)

        print(
            "[RAG] Question :",
            query
        )

        print("=" * 60)

        # =====================================================
        # 1. EMBEDDING DE LA QUESTION
        # =====================================================

        print(
            "[RAG] Génération embedding "
            "de la question..."
        )

        query_embedding = (
            self.embedding_service
            .generate_query_embedding(
                query
            )
        )

        if not query_embedding:

            raise RuntimeError(
                "Impossible de générer "
                "l'embedding de la question."
            )

        print(
            "[RAG] Embedding généré :",
            len(query_embedding),
            "dimensions"
        )

        # =====================================================
        # 2. RECHERCHE VECTORIELLE SUPABASE
        # =====================================================

        print(
            "[RAG] Recherche vectorielle "
            "dans Supabase..."
        )

        response = (

            self.supabase

            .rpc(

                "match_documents",

                {

                    "query_embedding":
                        query_embedding,

                    "match_threshold":
                        match_threshold,

                    "match_count":
                        match_count

                }

            )

            .execute()

        )

        documents = (
            response.data
            or []
        )

        print(
            "[RAG] Documents trouvés :",
            len(documents)
        )

        for index, document in enumerate(
            documents,
            start=1
        ):

            print(
                f"[RAG] Résultat {index} :",
                document.get(
                    "titre"
                )
            )

            print(
                "[RAG] Similarité :",
                document.get(
                    "similarity"
                )
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
                document.get(
                    "titre"
                )
                or
                "Document sans titre"
            )

            source = (
                document.get(
                    "organisme"
                )
                or
                "Source inconnue"
            )

            source_path = (
                document.get(
                    "source_path"
                )
                or
                ""
            )

            content = (
                document.get(
                    "content"
                )
                or
                ""
            )

            # Limiter la taille d'un document
            # envoyé à Gemini
            content = content[:6000]

            part = (
                f"DOCUMENT {index}\n"
                f"Titre : {title}\n"
                f"Source : {source}\n"
                f"URL : {source_path}\n\n"
                f"{content}"
            )

            context_parts.append(
                part
            )

        return (
            "\n\n"
            "========================================\n\n"
            .join(
                context_parts
            )
        )


    # =========================================================
    # GÉNÉRER UNE RÉPONSE À PARTIR DES SOURCES
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

        context = (
            self.build_context(
                documents
            )
        )

        prompt = f"""
Tu es SikaGlé, un assistant agricole intelligent.

Ta mission est d'aider les agriculteurs, producteurs,
éleveurs et acteurs du monde rural avec des réponses
simples, pratiques, compréhensibles et fiables.

QUESTION DE L'UTILISATEUR :

{query}


INFORMATIONS DOCUMENTAIRES DISPONIBLES :

{context}


INSTRUCTIONS IMPORTANTES :

1. Réponds principalement à partir des informations
   présentes dans les documents fournis.

2. Ne prétends jamais qu'une information provient
   des documents si elle n'y apparaît pas.

3. Si les documents ne permettent pas de répondre
   complètement, dis-le clairement.

4. Ne transforme pas automatiquement une étude réalisée
   dans un autre pays en recommandation spécifique
   pour le Bénin.

5. Si une étude concerne une région ou un pays précis,
   indique-le lorsque cette précision est importante.

6. Utilise un français simple et naturel.

7. Évite le jargon scientifique inutile.
   Si un terme technique est nécessaire, explique-le.

8. Donne d'abord une réponse directement utile,
   puis les explications importantes.

9. N'invente jamais de dosage d'engrais,
   de pesticide, de médicament vétérinaire
   ou de produit phytosanitaire.

10. Si une recommandation dépend du type de sol,
    de la culture, de la région ou d'autres informations
    manquantes, précise-le.

11. La réponse doit rester suffisamment courte
    pour être facilement lue sur WhatsApp.

12. Ne recopie pas les documents mot pour mot.
    Synthétise leur contenu.

13. Ne mets pas une longue bibliographie dans
    le corps de la réponse.

Réponds maintenant à la question.
"""

        print(
            "[RAG] Génération de la réponse "
            "avec Gemini..."
        )

        answer = (
            self.gemini.generate_text(
                prompt
            )
        )

        return answer


    # =========================================================
    # QUESTION COMPLÈTE :
    # RECHERCHE + GÉNÉRATION
    # =========================================================

    def answer(
        self,
        query: str,
        match_threshold: float = 0.20,
        match_count: int = 5
    ):

        # =====================================================
        # 1. RECHERCHE DOCUMENTAIRE
        # =====================================================

        documents = (
            self.search_documents(

                query=query,

                match_threshold=
                    match_threshold,

                match_count=
                    match_count

            )
        )

        # =====================================================
        # 2. GÉNÉRATION DE LA RÉPONSE
        # =====================================================

        answer = (
            self.generate_answer(
                query=query,
                documents=documents
            )
        )

        # =====================================================
        # 3. SOURCES UTILISÉES
        # =====================================================

        sources = []

        seen_sources = set()

        for document in documents:

            source_path = (
                document.get(
                    "source_path"
                )
            )

            if (
                source_path
                and
                source_path not in seen_sources
            ):

                seen_sources.add(
                    source_path
                )

                sources.append({

                    "title":
                        document.get(
                            "titre"
                        ),

                    "organization":
                        document.get(
                            "organisme"
                        ),

                    "url":
                        source_path,

                    "similarity":
                        document.get(
                            "similarity"
                        )

                })

        # =====================================================
        # 4. RÉSULTAT
        # =====================================================

        return {

            "status":
                "success",

            "query":
                query,

            "answer":
                answer,

            "documents_found":
                len(
                    documents
                ),

            "sources":
                sources

        }


# =========================================================
# TEST RAG COMPLET
# =========================================================

def test_rag():

    try:

        rag = (
            RAGService()
        )

        # =====================================================
        # QUESTION DE TEST
        # =====================================================

        question = (
            "Quel est l'effet de la matière organique "
            "et de la fertilisation sur la fertilité "
            "des sols ?"
        )

        # =====================================================
        # RAG COMPLET
        # =====================================================

        result = (
            rag.answer(

                query=question,

                match_threshold=0.20,

                match_count=5

            )
        )

        return result

    except Exception as e:

        print(
            "[RAG] Erreur :",
            e
        )

        return {

            "status":
                "error",

            "message":
                str(
                    e
                )

        }
