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
            "✅ Connexion Supabase initialisée."
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

        match_threshold: float = 0.3,

        match_count: int = 5

    ):

        # =====================================================
        # VALIDATION
        # =====================================================

        if not query or not query.strip():

            raise ValueError(
                "La question de recherche est vide."
            )

        print(
            f"[RAG] Recherche : {query}"
        )

        # =====================================================
        # 1. GÉNÉRATION EMBEDDING DE LA REQUÊTE
        # =====================================================

        print(
            "[RAG] Génération de l'embedding "
            "de la requête..."
        )

        query_embedding = (

            self.embedding_service

            .generate_query_embedding(

                query

            )

        )

        print(
            "[RAG] Embedding généré."
        )

        # =====================================================
        # 2. RECHERCHE VECTORIELLE SUPABASE
        # =====================================================

        print(
            "[RAG] Recherche vectorielle "
            "dans documents_rag..."
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
        # 3. VÉRIFIER LES RÉSULTATS
        # =====================================================

        if not response.data:

            print(
                "[RAG] Aucun document trouvé."
            )

            return []

        print(

            f"[RAG] "
            f"{len(response.data)} "
            f"document(s) trouvé(s)."

        )

        return response.data


# =========================================================
# TEST RAG
# =========================================================

def test_rag():

    try:

        # =====================================================
        # INITIALISER LE SERVICE
        # =====================================================

        rag = RAGService()

        # =====================================================
        # QUESTION DE TEST
        # =====================================================

        question = (

            "Comment cultiver "
            "le maïs au Bénin ?"

        )

        # =====================================================
        # RECHERCHE
        # =====================================================

        documents = (

            rag.search_documents(

                query=question,

                match_threshold=0.3,

                match_count=5

            )

        )

        # =====================================================
        # FORMATER LES RÉSULTATS
        # =====================================================

        results = []

        for document in documents:

            content = (

                document.get(
                    "content",
                    ""
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

                "content_preview":

                    content[:500]

            })

        # =====================================================
        # RÉSULTAT FINAL
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
            f"[RAG] Erreur : {e}"
        )

        return {

            "status":
                "error",

            "message":
                str(e)

        }
