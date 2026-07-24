import os

from google import genai


class GeminiEmbedding:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY est manquante."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.model = (
            "gemini-embedding-001"
        )

    def generate_embedding(
        self,
        text: str
    ):

        if not text or not text.strip():

            raise ValueError(
                "Le texte à encoder est vide."
            )

        result = (
            self.client.models.embed_content(

                model=self.model,

                contents=text

            )
        )

        if not result.embeddings:

            raise ValueError(
                "Aucun embedding généré."
            )

        return result.embeddings[0].values


def test_embedding():

    try:

        embedding_service = (
            GeminiEmbedding()
        )

        vector = (
            embedding_service
            .generate_embedding(
                "Comment cultiver le maïs au Bénin ?"
            )
        )

        return {

            "status":
                "success",

            "dimension":
                len(vector),

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
