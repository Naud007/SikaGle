from google import genai
import re

from app.core import settings
from app.knowledge_engine.rag.prompt_builder import (
    PromptBuilder,
)


class ResponseGenerator:
    """
    Génère une réponse avec Gemini
    à partir des passages récupérés
    dans la base vectorielle.
    """

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY n'est pas configurée."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = (
            settings.GEMINI_GENERATION_MODEL
        )

        self.prompt_builder = PromptBuilder()

    # =========================================================
    # NETTOYAGE DE LA RÉPONSE
    # =========================================================

    def _clean_response(
        self,
        text: str,
        input_type: str,
    ) -> str:

        if not text:
            return ""

        text = text.strip()

        input_type = (
            input_type or "text"
        ).lower().strip()

        # =====================================================
        # AUDIO
        # =====================================================

        if input_type == "audio":

            text = re.sub(
                r"\*\*(.*?)\*\*",
                r"\1",
                text,
                flags=re.DOTALL,
            )

            text = re.sub(
                r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)",
                r"\1",
                text,
                flags=re.DOTALL,
            )

            text = re.sub(
                r"^\s*#{1,6}\s*",
                "",
                text,
                flags=re.MULTILINE,
            )

            text = re.sub(
                r"^\s*[-•]\s+",
                "",
                text,
                flags=re.MULTILINE,
            )

            text = re.sub(
                r"^\s*\*\s+",
                "",
                text,
                flags=re.MULTILINE,
            )

            text = re.sub(
                r"^\s*\d+[\.\)]\s+",
                "",
                text,
                flags=re.MULTILINE,
            )

            text = re.sub(
                r"```.*?```",
                "",
                text,
                flags=re.DOTALL,
            )

            text = text.replace("[", "")
            text = text.replace("]", "")
            text = text.replace("{", "")
            text = text.replace("}", "")

            text = re.sub(
                r"[ \t]+",
                " ",
                text,
            )

            text = re.sub(
                r"\n{3,}",
                "\n\n",
                text,
            )

            return text.strip()

        # =====================================================
        # TEXTE / WHATSAPP
        # =====================================================

        text = re.sub(
            r"\*\*(.*?)\*\*",
            r"*\1*",
            text,
            flags=re.DOTALL,
        )

        text = re.sub(
            r"^\s*#{1,6}\s*",
            "",
            text,
            flags=re.MULTILINE,
        )

        text = re.sub(
            r"^\s*[-•]\s+",
            "* ",
            text,
            flags=re.MULTILINE,
        )

        text = re.sub(
            r"^\s*\d+[\.\)]\s+",
            "* ",
            text,
            flags=re.MULTILINE,
        )

        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            if (
                stripped.startswith("|")
                and stripped.endswith("|")
            ):
                continue

            if re.match(
                r"^\|?\s*:?-{3,}:?\s*"
                r"(\|\s*:?-{3,}:?\s*)+\|?$",
                stripped,
            ):
                continue

            cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        text = re.sub(
            r"\n\s+\* ",
            "\n* ",
            text,
        )

        lines = text.splitlines()
        repaired_lines = []

        for line in lines:

            if line.strip().startswith("* "):

                content = line.strip()[2:].strip()

                content = content.replace("*", "")

                repaired_lines.append(
                    "* " + content
                )

            else:

                if line.count("*") % 2 != 0:
                    line = line.replace("*", "")

                repaired_lines.append(line)

        text = "\n".join(repaired_lines)

        return text.strip()

    # =========================================================
    # GÉNÉRATION
    # =========================================================

    def generate(
        self,
        question: str,
        contexts: list[str],
        language: str = "fr",
        input_type: str = "text",
        weather_context: str | None = None,
        conversation_history: str | None = None,
        reasoning_summary: str | None = None,
    ) -> str:

        # -----------------------------------------------------
        # Construction du prompt
        # -----------------------------------------------------

        prompt = self.prompt_builder.build(
            question=question,
            contexts=contexts,
            language=language,
            input_type=input_type,
            weather_context=weather_context,
            conversation_history=conversation_history,
            reasoning_summary=reasoning_summary,
        )

        # -----------------------------------------------------
        # Appel Gemini
        # -----------------------------------------------------

        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        )

        # =====================================================
        # RÉCUPÉRATION EXPLICITE DU TEXTE GEMINI
        # =====================================================

        text_parts = []

        try:

            candidates = (
                response.candidates
                or []
            )

            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None,
                )

                if content is None:
                    continue

                parts = getattr(
                    content,
                    "parts",
                    [],
                )

                for part in parts:

                    text = getattr(
                        part,
                        "text",
                        None,
                    )

                    if text:

                        text_parts.append(
                            text
                        )

        except Exception:

            text_parts = []

        # =====================================================
        # RÉPONSE PRINCIPALE
        # =====================================================

        if text_parts:

            answer = "\n".join(
                text_parts
            ).strip()

            return self._clean_response(
                text=answer,
                input_type=input_type,
            )

        # =====================================================
        # FALLBACK
        # =====================================================

        if response.text:

            return self._clean_response(
                text=response.text.strip(),
                input_type=input_type,
            )

        return (
            "Je n'ai pas pu générer une réponse."
        )