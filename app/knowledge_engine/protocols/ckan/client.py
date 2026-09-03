from __future__ import annotations

import requests


class CKANClient:
    """
    Client générique pour communiquer avec un dépôt CKAN
    (International Institute of Tropical Agriculture — IITA,
    et potentiellement d'autres sources CKAN futures).

    Contrairement à Dataverse (où la licence nécessite un
    appel séparé par document via DataverseLicenseChecker),
    l'API CKAN inclut déjà la licence directement dans la
    réponse de chaque jeu de données (license_id, restriction,
    isopen) — pas besoin d'appel réseau supplémentaire.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 30,
    ):

        self.base_url = base_url.rstrip("/")

        self.timeout_seconds = timeout_seconds

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "SikaGle Knowledge Engine"
                )
            }
        )

    def list_package_names(
        self,
    ) -> list[str]:
        """
        Retourne la liste de TOUS les identifiants de jeux de
        données disponibles (pas leurs détails complets).
        """

        response = self.session.get(
            f"{self.base_url}/api/3/action/package_list",
            timeout=self.timeout_seconds,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "result",
            [],
        )

    def get_package_details(
        self,
        package_name: str,
    ) -> dict | None:
        """
        Retourne les détails complets d'UN jeu de données
        (titre, description, licence, ressources, etc.), ou
        None en cas d'échec (jeu de données supprimé/privé
        entre-temps, erreur réseau...).
        """

        try:

            response = self.session.get(
                f"{self.base_url}/api/3/action/"
                "package_show",
                params={
                    "id": package_name,
                },
                timeout=self.timeout_seconds,
            )

            if response.status_code != 200:

                return None

            data = response.json()

            if not data.get("success"):

                return None

            return data.get(
                "result"
            )

        except Exception as e:

            print(
                "[CKAN] Erreur lors de la "
                f"récupération de '{package_name}' : {e}"
            )

            return None