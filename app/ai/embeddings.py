import os

from google import genai


# =========================================================
# GEMINI EMBEDDING SERVICE
# =========================================================

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

        # Modèle d'embedding Gemini
        self.model = "gemini-embedding-001"

        # Dimension compatible avec pgvector
        # et l'index IVFFlat de Supabase
        self.dimension = 1536


    # =========================================================
    # GÉNÉRATION EMBEDDING
    # =========================================================

    def generate_embedding(
        self,
        text: str
    ) -> list[float]:

        if not text or not text.strip():

            raise ValueError(
                "Le texte à encoder est vide."
            )


        try:

            result = (

                self.client
                .models
                .embed_content(

                    model=self.model,

                    contents=text,

                    config={

                        "output_dimensionality":
                            self.dimension

                    }

                )

            )


        except Exception as e:

            raise RuntimeError(

                f"Erreur lors de la génération "
                f"de l'embedding Gemini : {e}"

            )


        if not result.embeddings:

            raise ValueError(

                "Aucun embedding généré "
                "par Gemini."

            )


        vector = (

            result
            .embeddings[0]
            .values

        )


        if not vector:

            raise ValueError(

                "L'embedding généré est vide."

            )


        # Vérification importante :
        # le vecteur doit correspondre
        # à vector(1536) dans Supabase

        if len(vector) != self.dimension:

            raise ValueError(

                f"Dimension inattendue : "
                f"{len(vector)}. "
                f"Dimension attendue : "
                f"{self.dimension}."

            )


        return vector


# =========================================================
# TEST EMBEDDING
# =========================================================

def test_embedding():

    try:

        embedding_service = (
            GeminiEmbedding()
        )


        test_text = (

            "Comment cultiver "
            "le maïs au Bénin ?"

        )


        vector = (

            embedding_service
            .generate_embedding(
                test_text
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
                embedding_service.dimension,

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
