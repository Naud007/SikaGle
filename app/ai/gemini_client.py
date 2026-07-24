import os

from google import genai


# =========================================================
# CONFIGURATION
# =========================================================

GEMINI_MODEL = "gemini-2.5-flash-lite"


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

        self.model = GEMINI_MODEL

        print(
            f"🔥 GEMINI MODEL ACTUEL : {self.model}"
        )


    # =========================================================
    # GÉNÉRATION DE TEXTE
    # =========================================================

    def generate_text(
        self,
        prompt: str
    ) -> str:

        print(
            "🤖 Gemini reçoit une requête..."
        )

        print(
            f"🤖 Modèle utilisé : {self.model}"
        )

        try:

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

            result = response.text.strip()

            print(
                "✅ Gemini a répondu avec succès."
            )

            return result


        except Exception as e:

            print(
                f"❌ Erreur Gemini : {str(e)}"
            )

            raise


# =========================================================
# TEST GEMINI
# =========================================================

def test_gemini():

    print(
        "=================================================="
    )

    print(
        "🧪 TEST GEMINI SikaGlé"
    )

    print(
        "=================================================="
    )


    try:

        gemini = GeminiClient()


        response = gemini.generate_text(

            """
Tu es SikaGlé, un assistant agricole intelligent
destiné aux producteurs agricoles du Bénin.

Réponds simplement et brièvement à la question suivante :

Dis bonjour au cultivateur et présente-toi
en une seule phrase.
"""

        )


        print(
            "✅ TEST GEMINI RÉUSSI"
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

        print(
            f"❌ TEST GEMINI ÉCHOUÉ : {str(e)}"
        )


        return {

            "status":
                "error",

            "model":
                GEMINI_MODEL,

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
