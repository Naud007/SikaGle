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

            # -------------------------------------------------
            # Gras Markdown
            # **texte** -> texte
            # -------------------------------------------------

            text = re.sub(
                r"\*\*(.*?)\*\*",
                r"\1",
                text,
                flags=re.DOTALL,
            )

            # -------------------------------------------------
            # Italique Markdown
            # *texte* -> texte
            # -------------------------------------------------

            text = re.sub(
                r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)",
                r"\1",
                text,
                flags=re.DOTALL,
            )

            # -------------------------------------------------
            # Titres Markdown
            # ## Titre -> Titre
            # -------------------------------------------------

            text = re.sub(
                r"^\s*#{1,6}\s*",
                "",
                text,
                flags=re.MULTILINE,
            )

            # -------------------------------------------------
            # Puces
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Listes numérotées
            # -------------------------------------------------

            text = re.sub(
                r"^\s*\d+[\.\)]\s+",
                "",
                text,
                flags=re.MULTILINE,
            )

            # -------------------------------------------------
            # Blocs de code
            # -------------------------------------------------

            text = re.sub(
                r"```.*?```",
                "",
                text,
                flags=re.DOTALL,
            )

            # -------------------------------------------------
            # Symboles Markdown inutiles pour la voix
            # -------------------------------------------------

            text = text.replace("[", "")
            text = text.replace("]", "")
            text = text.replace("{", "")
            text = text.replace("}", "")

            # -------------------------------------------------
            # Nettoyage des espaces
            # -------------------------------------------------

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

        # Gras Markdown -> italique WhatsApp
        text = re.sub(
            r"\*\*(.*?)\*\*",
            r"*\1*",
            text,
            flags=re.DOTALL,
        )

        # Titres Markdown
        text = re.sub(
            r"^\s*#{1,6}\s*",
            "",
            text,
            flags=re.MULTILINE,
        )

        # Tirets de liste -> liste WhatsApp
        text = re.sub(
            r"^\s*[-•]\s+",
            "* ",
            text,
            flags=re.MULTILINE,
        )

        # Listes numérotées -> liste WhatsApp
        text = re.sub(
            r"^\s*\d+[\.\)]\s+",
            "* ",
            text,
            flags=re.MULTILINE,
        )

        # Supprimer les tableaux Markdown
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

        # Espaces
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

        # Espaces avant/après les paragraphes
        text = re.sub(
            r"\n\s+\* ",
            "\n* ",
            text,
        )
                # -----------------------------------------------------
        # Réparer les astérisques Markdown mal fermés
        # -----------------------------------------------------

        lines = text.splitlines()
        repaired_lines = []

        for line in lines:

            # Une ligne de liste doit commencer par "* "
            if line.strip().startswith("* "):

                content = line.strip()[2:].strip()

                # Supprimer les astérisques isolés
                content = content.replace("*", "")

                repaired_lines.append(
                    "* " + content
                )

            else:

                # Pour les autres lignes, conserver uniquement
                # les astérisques correctement utilisés.
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
    ) -> str:

        # -----------------------------------------------------
        # Construction du prompt
        # -----------------------------------------------------

        prompt = self.prompt_builder.build(
            question=question,
            contexts=contexts,
            language=language,
            input_type=input_type,
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