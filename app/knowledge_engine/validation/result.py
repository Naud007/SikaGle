from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationResult:
    """
    Résultat de la validation d'un document.
    """

    valid: bool = True

    errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    def add_error(
        self,
        message: str,
    ) -> None:

        self.valid = False

        self.errors.append(message)

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(message)
