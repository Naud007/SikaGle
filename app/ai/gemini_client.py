import os

from google import genai


# =========================================================
# CLIENT GEMINI
# =========================================================

class GeminiClient:

    def __init__(self):

        # =====================================================
        # RÉCUPÉRER LA CLÉ API
        # =====================================================

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        )

        if not self.api_key:

            raise ValueError(
                "GEMINI_API_KEY est manquante."
            )


        # =====================================================
        # INITIALISER LE CLIENT GEMINI
        # =====================================================

        self.client = genai.Client(
            api_key=self.api_key
        )


        # =====================================================
        # MODÈLE GEMINI
        # =====================================================

        self.model = "gemini-1.5-flash"


        # =====================================================
        # LOG DE VÉRIFICATION
        # =====================================================

        print(
            "🔥 GEMINI MODEL ACTUEL :",
            self.model
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
            "🤖 Modèle utilisé :",
            self.model
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


            # =================================================
            # VÉRIFIER LA RÉPONSE
            # =================================================

            if not response.text:

                raise ValueError(

                    "Gemini n'a retourné "
                    "aucune réponse."

                )


            print(
                "✅ Réponse Gemini reçue."
            )


            return response.text.strip()


        except Exception as e:

            print(
                "❌ Erreur Gemini :",
                str(e)
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

        # -----------------------------------------------------
        # Créer le client
        # -----------------------------------------------------

        gemini = GeminiClient()


        # -----------------------------------------------------
        # Prompt de test
        # -----------------------------------------------------

        prompt = (

            "Réponds simplement et brièvement : "
            "SikaGlé fonctionne."

        )


        # -----------------------------------------------------
        # Envoyer la requête
        # -----------------------------------------------------

        response = (

            gemini
            .generate_text(
                prompt
            )

        )


        # -----------------------------------------------------
        # Résultat
        # -----------------------------------------------------

        print(
            "✅ TEST GEMINI RÉUSSI"
        )

        print(
            "Modèle :",
            gemini.model
        )

        print(
            "Réponse :",
            response
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
            "❌ TEST GEMINI ÉCHOUÉ :",
            str(e)
        )


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

    print(
        "=================================================="
    )

    print(
        "🔎 LISTE DES MODÈLES GEMINI"
    )

    print(
        "=================================================="
    )


    # =====================================================
    # RÉCUPÉRER LA CLÉ API
    # =====================================================

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

        # =================================================
        # INITIALISER CLIENT
        # =================================================

        client = genai.Client(

            api_key=api_key

        )


        models = []


        # =================================================
        # RÉCUPÉRER LES MODÈLES
        # =================================================

        for model in client.models.list():

            model_data = {

                "name":
                    model.name,

                "display_name":
                    getattr(

                        model,

                        "display_name",

                        None

                    )

            }


            models.append(
                model_data
            )


        print(

            f"✅ {len(models)} modèle(s) "
            f"Gemini trouvé(s)."

        )


        return {

            "status":
                "success",

            "models":
                models

        }


    except Exception as e:

        print(

            "❌ Erreur récupération "
            "des modèles Gemini :",

            str(e)

        )


        return {

            "status":
                "error",

            "message":
                str(e)

        }
