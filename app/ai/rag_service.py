import os

from supabase import create_client, Client

from app.ai.embeddings import (
    GeminiEmbeddingService
)


# =========================================================
# SERVICE RAG
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
                model="gemini-embedding-001",
                output_dimensionality=1536
            )
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
        # 1. VALIDATION
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
        # 2. EMBEDDING DE LA QUESTION
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
        # 3. RECHERCHE VECTORIELLE SUPABASE
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


        # =====================================================
        # 4. RÉSULTATS
        # =====================================================

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
# TEST RAG
# =========================================================

def test_rag():

    try:

        # =====================================================
        # 1. INITIALISER LE SERVICE
        # =====================================================

        rag = (
            RAGService()
        )


        # =====================================================
        # 2. QUESTION DE TEST
        #
        # Cette question correspond volontairement
        # aux documents FAO que nous venons d'ingérer.
        # =====================================================

        question = (
            "Quel est l'effet de la matière organique "
            "et de la fertilisation sur la fertilité "
            "des sols ?"
        )


        # =====================================================
        # 3. RECHERCHE
        # =====================================================

        documents = (
            rag.search_documents(

                query=question,

                # Seuil volontairement assez bas
                # pour notre premier test.
                match_threshold=0.20,

                match_count=5

            )
        )


        # =====================================================
        # 4. FORMATER LES RÉSULTATS
        # =====================================================

        results = []


        for document in documents:

            content = (
                document.get(
                    "content"
                )
                or
                ""
            )


            results.append({

                "id":
                    document.get(
                        "id"
                    ),

                "titre":
                    document.get(
                        "titre"
                    ),

                "organisme":
                    document.get(
                        "organisme"
                    ),

                "culture":
                    document.get(
                        "culture"
                    ),

                "zone_geographique":
                    document.get(
                        "zone_geographique"
                    ),

                "similarity":
                    document.get(
                        "similarity"
                    ),

                "source_path":
                    document.get(
                        "source_path"
                    ),

                "content_preview":
                    content[:1000]

            })


        # =====================================================
        # 5. RÉSULTAT FINAL
        # =====================================================

        return {

            "status":
                "success",

            "query":
                question,

            "results_count":
                len(
                    results
                ),

            "results":
                results

        }


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
