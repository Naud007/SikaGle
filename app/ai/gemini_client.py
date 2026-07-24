import os

from google import genai


# =========================================================
# CLIENT GEMINI
# =========================================================

class GeminiClient:

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

        # =====================================================
        # MODÈLE GEMINI
        # =====================================================
        #
        # Modèle utilisé pour les réponses quotidiennes
        # de SikaGlé.
        #
        # Nous testons actuellement Gemini 1.5 Flash.
        #

        self.model = "gemini-1.5-flash"


    # =========================================================
    # GÉNÉRATION DE TEXTE
    # =========================================================

    def generate_text(
        self,
        prompt: str
    ) -> str:

        response = (

            self.client
            .models
            .generate_content(

                model=self.model,

                contents=prompt

            )

        )

        if not response.text:

            raise ValueError(

                "Gemini n'a retourné "
                "aucune réponse."

            )

        return response.text.strip()


# =========================================================
# TEST GEMINI
# =========================================================

def test_gemini():

    try:

        gemini = GeminiClient()

        response = gemini.generate_text(

            "Réponds simplement : "
            "SikaGlé fonctionne."

        )

        return {

            "status":
                "success",

            "model":
                gemini.model,

            "response":
                response

        }


    except Exception as e:

        return {

            "status":
                "error",

            "model":
                "gemini-1.5-flash",

            "message":
                str(e)

        }


# =========================================================
# LISTE DES MODÈLES GEMINI DISPONIBLES
# =========================================================

def list_gemini_models():

    api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    if not api_key:

        return {

            "status":
                "error",

            "message":
                "GEMINI_API_KEY manquante"

        }


    try:

        client = genai.Client(

            api_key=api_key

        )


        models = []


        for model in client.models.list():

            models.append({

                "name":
                    model.name,

                "display_name":
                    getattr(

                        model,

                        "display_name",

                        None

                    )

            })


        return {

            "status":
                "success",

            "models":
                models

        }


    except Exception as e:

        return {

            "status":
                "error",

            "message":
                str(e)

        }
