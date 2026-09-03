from __future__ import annotations

import requests


class DataverseLicenseChecker:
    """
    Vérifie la licence réelle d'un dataset Dataverse (Harvard
    Dataverse ou toute autre instance, ex: ICRISAT), via l'API
    native Dataverse, qui expose un champ "license" structuré
    contrairement à OAI-PMH (dc:rights systématiquement absent
    des métadonnées, vérifié en test réel le 31/08/2026).

    Réutilisable pour toute source hébergée sur Dataverse
    (AfricaRice, IRRI, Bioversity/CIAT, CIFOR, ICRISAT...), pas
    spécifique à un connecteur en particulier.
    """

    # Licences considérées comme utilisables commercialement.
    # CC0 (domaine public) et CC-BY (attribution simple) sont
    # sûres ; on exclut volontairement tout ce qui contient
    # NC (non-commercial), ND (pas de dérivés) ou SA
    # (partage à l'identique, qui pourrait obliger à republier
    # nos propres contenus sous la même licence).

    PERMISSIVE_LICENSE_KEYWORDS = [
        "cc0",
        "public domain",
        "cc-by",
        "cc by",
    ]

    RESTRICTIVE_LICENSE_KEYWORDS = [
        "nc",
        "non-commercial",
        "noncommercial",
        "nd",
        "no derivatives",
        "sa",
        "share-alike",
        "sharealike",
    ]

    def __init__(
        self,
        base_url: str = "https://dataverse.harvard.edu",
        timeout_seconds: int = 20,
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

    def is_license_permissive(
        self,
        doi_or_identifier: str,
    ) -> bool | None:
        """
        Retourne True si la licence du dataset est permissive
        (CC0/CC-BY), False si elle est restrictive (NC/ND/SA),
        ou None si la licence n'a pas pu être déterminée (dans
        ce cas, l'appelant doit choisir prudemment de NE PAS
        ingérer le document, faute de certitude).
        """

        persistent_id = self._normalize_doi(
            doi_or_identifier
        )

        if not persistent_id:

            return None

        try:

            response = self.session.get(
                f"{self.base_url}/api/datasets/"
                ":persistentId/",
                params={
                    "persistentId":
                        persistent_id,
                },
                timeout=self.timeout_seconds,
            )

            if response.status_code != 200:

                return None

            data = response.json()

            license_info = (
                data
                .get("data", {})
                .get("latestVersion", {})
                .get("license", {})
            )

            # =====================================================
            # CORRECTIF (02/09/2026) :
            #
            # Harvard Dataverse renvoie la licence comme un objet
            # structuré ({"name": "CC0 1.0", "uri": "..."}), mais
            # l'instance ICRISAT (indépendante) la renvoie parfois
            # comme un simple texte ("CC0 1.0"). On gère les deux
            # formats pour éviter de rejeter systématiquement tous
            # les documents à cause d'une erreur de lecture, plutôt
            # que d'une vraie décision de licence.
            # =====================================================

            if isinstance(license_info, str):

                license_name = (
                    license_info or ""
                ).lower()

            else:

                license_name = (
                    license_info.get("name")
                    or ""
                ).lower()

            if not license_name:

                return None

            if any(
                keyword in license_name
                for keyword in self.RESTRICTIVE_LICENSE_KEYWORDS
            ):

                return False

            if any(
                keyword in license_name
                for keyword in self.PERMISSIVE_LICENSE_KEYWORDS
            ):

                return True

            # Licence reconnue mais ambiguë (ni clairement
            # permissive, ni clairement restrictive) : on
            # reste prudent et on refuse par défaut.

            return None

        except Exception as e:

            print(
                "[DATAVERSE LICENSE] Vérification "
                f"impossible pour {persistent_id} : {e}"
            )

            return None

    def _normalize_doi(
        self,
        raw_identifier: str,
    ) -> str | None:
        """
        Transforme un identifiant sous différentes formes
        (ex: "doi:10.7910/DVN/XXX", "https://doi.org/10.7910/...")
        vers le format attendu par l'API Dataverse : "doi:10.xxx/...".
        """

        if not raw_identifier:

            return None

        value = raw_identifier.strip()

        if value.startswith("doi:"):

            return value

        if "doi.org/" in value:

            doi_part = value.split(
                "doi.org/",
                1,
            )[1]

            return f"doi:{doi_part}"

        return None