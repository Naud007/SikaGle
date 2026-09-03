from __future__ import annotations

from datetime import date

from app.schemas.document import DocumentMetadata


class CKANNormalizer:
    """
    Transforme un jeu de données CKAN brut (dict retourné par
    CKANClient.get_package_details) en DocumentMetadata.
    """

    # =========================================================
    # LICENCES CONSIDÉRÉES PERMISSIVES (utilisables
    # commercialement), même logique que
    # DataverseLicenseChecker pour rester cohérent.
    # =========================================================

    PERMISSIVE_LICENSE_IDS = {
        "cc-by",
        "cc-by-4.0",
        "cc-zero",
        "cc0-1.0",
        "other-open",
    }

    def is_license_permissive(
        self,
        package: dict,
    ) -> bool:
        """
        CKAN inclut déjà la licence directement dans la
        réponse (license_id, isopen) — pas d'appel réseau
        séparé nécessaire, contrairement à Dataverse.
        """

        license_id = (
            package.get(
                "license_id",
                "",
            )
            or ""
        ).lower()

        is_open_flag = bool(
            package.get(
                "isopen",
                False,
            )
        )

        return (
            is_open_flag
            and license_id
            in self.PERMISSIVE_LICENSE_IDS
        )

    def normalize(
        self,
        package: dict,
        source: str = "IITA",
    ) -> DocumentMetadata:

        title = (
            package.get("title")
            or package.get("name")
            or "Sans titre"
        )

        description = (
            package.get("notes")
            or package.get("source")
            or None
        )

        # =====================================================
        # AUTEURS
        # =====================================================

        author_field = (
            package.get("author")
            or package.get(
                "contributor_person_2_affiliation"
            )
        )

        authors = (
            [author_field]
            if author_field
            else []
        )

        # =====================================================
        # MOTS-CLÉS (tags CKAN)
        # =====================================================

        keywords = [
            tag.get("display_name")
            or tag.get("name")
            for tag in package.get(
                "tags",
                [],
            )
            if tag.get("display_name")
            or tag.get("name")
        ]

        # =====================================================
        # DATE
        # =====================================================

        published_at = None

        metadata_created = package.get(
            "metadata_created"
        )

        if metadata_created:

            try:

                published_at = date.fromisoformat(
                    metadata_created[:10]
                )

            except ValueError:

                pass

        # =====================================================
        # URL
        # =====================================================

        package_id = package.get(
            "id",
            "",
        )

        url = (
            f"https://data.iita.org/dataset/{package_id}"
            if package_id
            else "https://data.iita.org"
        )

        return DocumentMetadata(
            title=title,
            source=source,
            url=url,
            published_at=published_at,
            language=None,
            document_type="dataset",
            description=description,
            keywords=keywords,
            author=(
                authors[0]
                if authors
                else None
            ),
            authors=authors,
            publisher="IITA",
            identifier=package.get(
                "name"
            ),
        )