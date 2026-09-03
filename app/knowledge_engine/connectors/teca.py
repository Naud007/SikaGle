from __future__ import annotations

from datetime import date

import requests
from bs4 import BeautifulSoup

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.schemas.document import DocumentMetadata


class TECAConnector(BaseConnector):
    """
    Connecteur pour TECA (Technologies and Practices for Small
    Agricultural Producers), plateforme FAO de fiches PRATIQUES
    destinées directement aux petits producteurs — contrairement
    aux autres sources déjà intégrées (FAO AGRIS, AfricaRice,
    IRRI, IITA...), qui sont des articles scientifiques.

    NOTE (autorisation, 03/09/2026) : TECA n'a pas de mécanisme
    d'accès en masse public (pas d'OAI-PMH, pas d'API REST
    documentée) — l'API utilisée ici (teca.review.fao.org) est
    celle appelée en coulisses par leur propre interface web, et
    son usage pour SikaGlé a été explicitement autorisé par la
    FAO (teca@fao.org) suite à une demande écrite. Contrairement
    aux sources Dataverse, il n'y a pas de vérification de
    licence par document ici, l'autorisation ayant été obtenue
    directement auprès de l'éditeur (FAO).

    NOTE (technique) : contrairement aux autres connecteurs, TOUT
    le catalogue (998 fiches au 03/09/2026) est renvoyé en UN
    SEUL appel — pas de pagination, pas d'étape de découverte
    séparée par identifiant.
    """

    API_URL = (
        "https://teca.review.fao.org/api/"
        "collections/get/technologies"
    )

    def __init__(self):
        super().__init__("teca")

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        response = requests.get(
            self.API_URL,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        entries = data.get(
            "entries",
            [],
        )

        print(
            f"[TECA] {len(entries)} fiches "
            "reçues depuis l'API."
        )

        documents: list[DocumentMetadata] = []

        for entry in entries:

            document = self._normalize(
                entry
            )

            if document is not None:

                documents.append(
                    document
                )

        return documents

    # =========================================================
    # NORMALISATION
    # =========================================================

    def _normalize(
        self,
        entry: dict,
    ) -> DocumentMetadata | None:

        title = (
            entry.get("title")
            or entry.get("tittle")
            or ""
        ).strip()

        if not title:

            return None

        description_html = (
            entry.get("description")
            or ""
        )

        description_text = (
            self._strip_html(
                description_html
            )
        )

        summary = (
            entry.get("summary")
            or ""
        ).strip()

        full_content = (
            f"{summary}\n\n{description_text}"
            if summary
            else description_text
        )

        # =====================================================
        # LANGUE
        # =====================================================

        languages = entry.get(
            "language",
            [],
        )

        language = (
            languages[0]
            if languages
            else None
        )

        # =====================================================
        # MOTS-CLÉS (fusion keywords + agrovoc + tags)
        # =====================================================

        keywords = list(
            entry.get(
                "keywords",
                [],
            )
            or []
        )

        for agrovoc_entry in entry.get(
            "agrovoc_keywords",
            [],
        ) or []:

            display = agrovoc_entry.get(
                "display",
                ""
            )

            if display:

                keywords.append(
                    display.split("#")[0]
                )

        # =====================================================
        # CATÉGORIES / CULTURE
        # =====================================================

        categories = entry.get(
            "categories",
            [],
        ) or []

        category_names = [
            category.get("name", "")
            for category in categories
            if category.get("name")
        ]

        # =====================================================
        # PAYS / RÉGION
        # =====================================================

        region = entry.get(
            "region",
            [],
        )

        location = entry.get(
            "location",
            ""
        )

        # =====================================================
        # DATE
        # =====================================================

        published_at = (
            self._parse_publication_date(
                entry.get(
                    "publication_date"
                )
            )
        )

        # =====================================================
        # URL
        # =====================================================

        entry_id = entry.get(
            "id",
            ""
        )

        url = (
            f"https://teca.apps.fao.org/en/"
            f"technologies/{entry_id}/"
            if entry_id
            else "https://teca.apps.fao.org"
        )

        return DocumentMetadata(
            title=title,
            source="TECA (FAO)",
            url=url,
            published_at=published_at,
            language=language,
            document_type="practice",
            description=full_content,
            keywords=keywords,
            author=entry.get("source"),
            authors=(
                [entry.get("source")]
                if entry.get("source")
                else []
            ),
            publisher="FAO TECA",
            identifier=(
                f"teca-{entry_id}"
            ),
        )

    # =========================================================
    # NETTOYAGE HTML
    # =========================================================

    @staticmethod
    def _strip_html(
        html_content: str,
    ) -> str:

        if not html_content:

            return ""

        soup = BeautifulSoup(
            html_content,
            "html.parser",
        )

        text = soup.get_text(
            separator="\n",
        )

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        return "\n".join(lines)

    # =========================================================
    # DATE
    # =========================================================

    @staticmethod
    def _parse_publication_date(
        raw_date,
    ) -> date | None:

        if not raw_date:

            return None

        try:

            import re

            match = re.search(
                r"\d{4}",
                str(raw_date),
            )

            if match:

                year = int(
                    match.group(0)
                )

                return date(
                    year,
                    1,
                    1,
                )

        except Exception:

            pass

        return None


registry.register(
    "teca",
    TECAConnector,
)