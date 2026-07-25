import os

from supabase import create_client, Client

from app.ai.embeddings import GeminiEmbedding


# =========================================================
# CONFIGURATION SUPABASE
# =========================================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    ""
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    ""
)


# =========================================================
# SERVICE RAG
# =========================================================

class RAGService:

    def __init__(self):

        if not SUPABASE_URL:

            raise ValueError(
                "SUPABASE_URL est manquante."
            )

        if not SUPABASE_KEY:

            raise ValueError(
                "SUPABASE_KEY est manquante."
            )


        self.supabase: Client = create_client(

            SUPABASE_URL,

            SUPABASE_KEY

        )


        self.embedding_service = (
            GeminiEmbedding()
        )


    # =====================================================
    # RECHERCHE VECTORIELLE
    # =====================================================

    def search_documents(

        self,

        query: str,

        match_threshold: float = 0.5,

        match_count: int = 5

    ):

        if not query or not query.strip():

            raise ValueError(

                "La question de recherche "
                "est vide."

            )


        # ---------------------------------------------
        # 1. Transformer la question en embedding
        # ---------------------------------------------

        query_embedding = (

            self.embedding_service
            .generate_embedding(
                query
            )

        )


        # ---------------------------------------------
        # 2. Recherche dans pgvector
        # ---------------------------------------------

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


        if not response.data:

            return []


        return response.data


# =========================================================
# TEST RAG
# =========================================================

def test_rag():

    try:

        rag = RAGService()


        question = (

            "Comment cultiver "
            "le maïs au Bénin ?"

        )


        documents = (

            rag.search_documents(

                query=question,

                match_threshold=0.3,

                match_count=5

            )

        )


        results = []


        for document in documents:

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
                    (
                        document
                        .get(
                            "content",
                            ""
                        )
                    )[:500]

            })


        return {

            "status":
                "success",

            "query":
                question,

            "results_count":
                len(results),

            "results":
                results

        }


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
