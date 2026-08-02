"""
SikaGlé

Validation des entrées utilisateur.
"""


class InputValidator:
    """
    Fournit des validations simples pour les données
    reçues par la plateforme.
    """

    @staticmethod
    def not_empty(value: str) -> bool:
        """
        Vérifie qu'une chaîne n'est pas vide.
        """

        return (
            isinstance(value, str)
            and value.strip() != ""
        )

    @staticmethod
    def max_length(
        value: str,
        maximum: int,
    ) -> bool:
        """
        Vérifie qu'une chaîne respecte
        une longueur maximale.
        """

        if not isinstance(value, str):
            return False

        return len(value) <= maximum
