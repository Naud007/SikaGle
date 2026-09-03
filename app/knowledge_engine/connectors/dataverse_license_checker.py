from __future__ import annotations

import requests


class DataverseLicenseChecker:
    """
    Vérifie la licence réelle d'un dataset Dataverse (Harvard
    Dataverse ou toute autre instance, ex: ICRISAT), via l'API
    native Dataverse.

    NOTE (correctif, 02/09/2026) : certaines instances (Harvard)
    renseignent un champ "license" structuré. D'autres (ICRISAT)
    laissent ce champ à "NONE" et décrivent la vraie licence en
    texte libre dans le champ "termsOfUse" à la place. On vérifie
    donc les deux, dans cet ordre.

    NOTE (correctif, 02/09/2026) : les mots-clés de détection
    utilisent des EXPRESSIONS COMPLÈTES ("non-commercial", pas
    juste "nc") plutôt que des fragments courts, car chercher de
    courts fragments ("nc", "sa", "nd") dans du texte libre long
    (comme termsOfUse) produirait de faux positifs fréquents
    (ex: "nc" apparaît dans "since", "instance" ; "sa" dans "usa",
    "data" ; "nd" dans "and").
    """

    PERMISSIVE_LICENSE_KEYWORDS = [
        "cc0",
        "public domain",
        "creative commons zero",
        "cc-by",
        "cc by",
        "creative commons attribution",
    ]

    RESTRICTIVE_LICENSE_KEYWORDS = [
        "non-commercial",
        "noncommercial",
        "non commercial",
        "no derivatives",
        "noderivatives",
        "share-alike",
        "sharealike",
        "share alike",
        "cc-by-nc",
        "cc by nc",
        "cc-by-nd",
        "cc by nd",
        "cc-by-sa",
        "cc by sa",
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

        IMPORTANT : la détection de licence restrictive est
        vérifiée EN PREMIER, sur l'ensemble du texte disponible
        (licence structurée + termsOfUse). "CC-BY-NC" contient
        "cc-by" (permissif) ET "non-commercial" (restrictif) —
        si on vérifiait le permissif en premier, une licence
        CC-BY-NC serait faussement acceptée comme permissive.
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

            latest_version = (
                data
                .get("data", {})
                .get("latestVersion", {})
            )

            license_info = (
                latest_version.get(
                    "license",
                    {},
                )
            )

            if isinstance(license_info, str):

                license_text = (
                    license_info or ""
                )

            else:

                license_text = (
                    license_info.get("name")
                    or ""
                )

            # =====================================================
            # REPLI : champ "license" absent ou vide ("NONE")
            # → on cherche la vraie information dans termsOfUse
            # (texte libre), pratique observée sur ICRISAT.
            # =====================================================

            if (
                not license_text
                or license_text.strip().lower()
                == "none"
            ):

                license_text = (
                    latest_version.get(
                        "termsOfUse",
                        "",
                    )
                    or ""
                )

            license_text = license_text.lower()

            if not license_text:

                return None

            if any(
                keyword in license_text
                for keyword in self.RESTRICTIVE_LICENSE_KEYWORDS
            ):

                return False

            if any(
                keyword in license_text
                for keyword in self.PERMISSIVE_LICENSE_KEYWORDS
            ):

                return True

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