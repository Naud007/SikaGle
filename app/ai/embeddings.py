import os

from google import genai
from google.genai import types


class GeminiEmbeddingService:

    def __init__(
        self,
        model="gemini-embedding-001",
        output_dimensionality=1536
    ):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

        self.output_dimensionality = (
            output_dimensionality
        )


    # =========================================================
    # EMBEDDING DOCUMENT
    # =========================================================

    def generate_document_embedding(
        self,
        text: str
    ):

        if (
            not text
            or not text.strip()
        ):

            raise ValueError(
                "Le texte à encoder est vide."
            )

        result = (
            self.client.models.embed_content(

                model=self.model,

                contents=text,

                config=(
                    types.EmbedContentConfig(

                        task_type=
                            "RETRIEVAL_DOCUMENT",

                        output_dimensionality=(
                            self.output_dimensionality
                        )

                    )
                )

            )
        )

        if (
            not result.embeddings
            or not result.embeddings[0].values
        ):

            raise ValueError(
                "Aucun embedding document généré."
            )

        return (
            result
            .embeddings[0]
            .values
        )


    # =========================================================
    # EMBEDDING REQUÊTE
    # =========================================================

    def generate_query_embedding(
        self,
        text: str
    ):

        if (
            not text
            or not text.strip()
        ):

            raise ValueError(
                "La requête à encoder est vide."
            )

        result = (
            self.client.models.embed_content(

                model=self.model,

                contents=text,

                config=(
                    types.EmbedContentConfig(

                        task_type=
                            "RETRIEVAL_QUERY",

                        output_dimensionality=(
                            self.output_dimensionality
                        )

                    )
                )

            )
        )

        if (
            not result.embeddings
            or not result.embeddings[0].values
        ):

            raise ValueError(
                "Aucun embedding de requête généré."
            )

        return (
            result
            .embeddings[0]
            .values
        )


# =========================================================
# TEST EMBEDDING
# =========================================================

def test_embedding():

    try:

        embedding_service = (
            GeminiEmbeddingService()
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
                vector[:5]

        }


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
