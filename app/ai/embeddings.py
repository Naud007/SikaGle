from app.knowledge_engine.embeddings.embedding_service import (
    JinaEmbeddingService,
)


# =========================================================
# SERVICE EMBEDDING — COMPATIBILITÉ
# =========================================================

GeminiEmbeddingService = JinaEmbeddingService
GeminiEmbedding = JinaEmbeddingService


# =========================================================
# TEST EMBEDDING
# =========================================================

def test_embedding():

    try:

        embedding_service = (
            JinaEmbeddingService()
        )

        vector = (
            embedding_service
            .generate_document_embedding(
                "Comment cultiver "
                "le maïs au Bénin ?"
            )
        )

        return {

            "status":
                "success",

            "model":
                embedding_service.model,

            "dimension":
                len(vector),

            "expected_dimension":
                embedding_service
                .output_dimensionality,

            "preview":
                vector[:5],

        }

    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e),

        }