from __future__ import annotations

from app.knowledge_engine.validation.result import (
    ValidationResult,
)


class DocumentValidator:
    """
    Vérifie qu'un document est exploitable
    avant son indexation.
    """

    MIN_CHARACTERS = 500

    MIN_CHUNKS = 1

    def validate(
        self,
        text: str,
        chunks: list[str],
    ) -> ValidationResult:

        result = ValidationResult()

        if not text.strip():

            result.add_error(
                "Le document est vide."
            )

            return result

        if len(text) < self.MIN_CHARACTERS:

            result.add_error(
                (
                    "Le document contient "
                    f"moins de {self.MIN_CHARACTERS} caractères."
                )
            )

        if len(chunks) < self.MIN_CHUNKS:

            result.add_error(
                "Aucun chunk généré."
            )

        if len(text) < 2000:

            result.add_warning(
                "Document très court."
            )

        return result
