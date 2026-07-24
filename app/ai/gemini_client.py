import os
from google import genai


def list_gemini_models():

    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        return {
            "status": "error",
            "message": "GEMINI_API_KEY manquante"
        }

    try:

        client = genai.Client(
            api_key=api_key
        )

        models = []

        for model in client.models.list():

            models.append({
                "name": model.name,
                "display_name": getattr(
                    model,
                    "display_name",
                    None
                )
            })

        return {
            "status": "success",
            "models": models
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
