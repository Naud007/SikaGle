import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self, xml_path):
        self.xml_path = xml_path

    def parse(self):

        print(
            f"[FAO DATASET PARSER] "
            f"Lecture : {self.xml_path.name}"
        )

        try:

            tree = ET.parse(
                self.xml_path
            )

            root = tree.getroot()

        except Exception as e:

            print(
                f"[FAO DATASET PARSER] "
                f"Erreur lecture XML : {e}"
            )

            return []

        # Namespaces AGRIS
        namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "agr": "http://purl.org/agris/1.0/",
            "oai": "http://www.openarchives.org/OAI/2.0/",
            "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        }

        documents = []

        # Recherche de toutes les notices potentielles
        records = root.findall(
            ".//oai:record",
            namespaces
        )

        print(
            f"[FAO DATASET PARSER] "
            f"{len(records)} notice(s) OAI trouvée(s)."
        )

        # Si le XML n'utilise pas OAI-PMH,
        # on cherche directement les éléments metadata
        if not records:

            metadata_elements = root.findall(
                ".//oai_dc:dc",
                namespaces
            )

            print(
                f"[FAO DATASET PARSER] "
                f"{len(metadata_elements)} bloc(s) metadata trouvé(s)."
            )

            for metadata in metadata_elements:

                document = self._parse_metadata(
                    metadata,
                    namespaces
                )

                if document:

                    documents.append(
                        document
                    )

        else:

            for record in records:

                metadata = record.find(
                    ".//oai_dc:dc",
                    namespaces
                )

                if metadata is None:

                    continue

                document = self._parse_metadata(
                    metadata,
                    namespaces
                )

                if document:

                    documents.append(
                        document
                    )

        print(
            f"[FAO DATASET PARSER] "
            f"{len(documents)} document(s) analysé(s)."
        )

        return documents

    def _parse_metadata(
        self,
        metadata,
        namespaces
    ):

        # -------------------------------------------------
        # TITRE
        # -------------------------------------------------

        title = self._get_first_text(
            metadata,
            [
                "dc:title",
            ],
            namespaces
        )

        if not title:

            title = "Document AGRIS"

        # -------------------------------------------------
        # DESCRIPTION / RÉSUMÉ
        # -------------------------------------------------

        description = self._get_first_text(
            metadata,
            [
                "dc:description",
            ],
            namespaces
        )

        # -------------------------------------------------
        # AUTEUR
        # -------------------------------------------------

        creators = self._get_all_text(
            metadata,
            [
                "dc:creator",
            ],
            namespaces
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        published_at = self._get_first_text(
            metadata,
            [
                "dc:date",
                "dct:issued",
                "dct:date",
            ],
            namespaces
        )

        # -------------------------------------------------
        # IDENTIFIANT
        # -------------------------------------------------

        identifier = self._get_first_text(
            metadata,
            [
                "dc:identifier",
                "dct:identifier",
            ],
            namespaces
        )

        # -------------------------------------------------
        # URL
        # -------------------------------------------------

        url = self._extract_url(
            metadata,
            namespaces
        )

        # Si aucune URL n'est disponible,
        # on utilise l'identifiant s'il s'agit d'une URL
        if not url and identifier:

            if identifier.startswith(
                ("http://", "https://")
            ):

                url = identifier

        # Pour DocumentMetadata, l'URL semble obligatoire.
        # On ignore donc les notices sans URL exploitable.
        if not url:

            return None

        # -------------------------------------------------
        # MOTS-CLÉS
        # -------------------------------------------------

        subjects = self._get_all_text(
            metadata,
            [
                "dc:subject",
            ],
            namespaces
        )

        # -------------------------------------------------
        # TYPE
        # -------------------------------------------------

        document_type = self._get_first_text(
            metadata,
            [
                "dc:type",
            ],
            namespaces
        )

        # -------------------------------------------------
        # SOURCE
        # -------------------------------------------------

        source = "FAO AGRIS"

        # -------------------------------------------------
        # CRÉATION DU DOCUMENT
        # -------------------------------------------------

        data = {
            "title": title,
            "url": url,
            "description": description,
            "source": source,
        }

        # Ajouter les champs seulement
        # s'ils existent dans DocumentMetadata

        if creators:

            data["authors"] = creators

        if published_at:

            data["published_at"] = published_at

        if subjects:

            data["keywords"] = subjects

        if document_type:

            data["document_type"] = document_type

        try:

            return DocumentMetadata(
                **data
            )

        except Exception as e:

            print(
                f"[FAO DATASET PARSER] "
                f"Document ignoré : {e}"
            )

            return None

    # =====================================================
    # OUTILS
    # =====================================================

    def _get_first_text(
        self,
        element,
        paths,
        namespaces
    ):

        for path in paths:

            child = element.find(
                path,
                namespaces
            )

            if (
                child is not None
                and child.text
            ):

                return child.text.strip()

        return None

    def _get_all_text(
        self,
        element,
        paths,
        namespaces
    ):

        values = []

        for path in paths:

            elements = element.findall(
                path,
                namespaces
            )

            for item in elements:

                if (
                    item is not None
                    and item.text
                ):

                    text = item.text.strip()

                    if text:

                        values.append(
                            text
                        )

        return values

    def _extract_url(
        self,
        metadata,
        namespaces
    ):

        # Chercher d'abord les identifiants
        # qui sont directement des URLs.

        identifiers = self._get_all_text(
            metadata,
            [
                "dc:identifier",
                "dct:identifier",
            ],
            namespaces
        )

        for identifier in identifiers:

            if identifier.startswith(
                ("http://", "https://")
            ):

                return identifier

        # Chercher ensuite les URLs dans
        # les éléments relation / source.

        relations = self._get_all_text(
            metadata,
            [
                "dc:relation",
                "dct:isPartOf",
                "dct:references",
            ],
            namespaces
        )

        for relation in relations:

            if relation.startswith(
                ("http://", "https://")
            ):

                return relation

        return None
