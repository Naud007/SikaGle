import os

from google import genai
from google.genai import types


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

        self.model = "gemini-2.5-flash"

    def generate_text(
        self,
        prompt: str
    ) -> str:

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt

        )

        if not response.text:

            raise ValueError(
                "Gemini n'a retourné aucune réponse."
            )

        return response.text.strip()


def test_gemini():

    try:

        gemini = GeminiClient()

        response = gemini.generate_text(
            "Réponds simplement : SikaGlé fonctionne."
        )

        return {
            "status": "success",
            "response": response
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }
