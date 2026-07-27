import re
import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS.

        Le dataset est traité directement en mémoire.
        Aucun stockage local n'est nécessaire.

        Objectifs :
        - extraire les notices AGRIS ;
        - conserver les métadonnées disponibles ;
        - ne jamais inventer un pays, une langue ou une culture ;
        - produire un contenu exploitable par le RAG.
        """
        pass


    # =========================================================
    # PARSER PRINCIPAL
    # =========================================================

    def parse(
        self,
        xml_content,
        filename=None,
        source_url=None
    ):

        print("=" * 60)
        print(
            "[FAO DATASET PARSER] "
            f"Analyse : {filename or 'dataset XML'}"
        )
        print("=" * 60)

        documents = []

        try:

            # =================================================
            # 1. VÉRIFIER LE CONTENU
            # =================================================

            if not xml_content:

                print(
                    "[FAO DATASET PARSER] "
                    "Contenu XML vide."
                )

                return []


            # =================================================
            # 2. CHARGER LE XML
            # =================================================

            if isinstance(
                xml_content,
                bytes
            ):

                print(
                    "[FAO DATASET PARSER] "
                    f"XML bytes : "
                    f"{len(xml_content)} octets"
                )

                root = ET.fromstring(
                    xml_content
                )


            elif isinstance(
                xml_content,
                str
            ):

                print(
                    "[FAO DATASET PARSER] "
                    f"XML texte : "
                    f"{len(xml_content)} caractères"
                )

                root = ET.fromstring(
                    xml_content
                )


            elif hasattr(
                xml_content,
                "read"
            ):

                tree = ET.parse(
                    xml_content
                )

                root = tree.getroot()


            else:

                raise ValueError(
                    "Format XML non supporté : "
                    f"{type(xml_content).__name__}"
                )


            print(
                "[FAO DATASET PARSER] "
                f"Root : {root.tag}"
            )


            # =================================================
            # 3. NAMESPACES AGRIS
            # =================================================

            namespaces = {

                "dc":
                    "http://purl.org/dc/elements/1.1/",

                "dct":
                    "http://purl.org/dc/terms/",

                "dctypes":
                    "http://purl.org/dc/dcmitype/",

                "dcat":
                    "http://www.w3.org/ns/dcat#",

                "xsi":
                    "http://www.w3.org/2001/XMLSchema-instance",

            }


            # =================================================
            # 4. RECHERCHER LES NOTICES
            # =================================================

            records = root.findall(
                ".//dctypes:BibliographicResource",
                namespaces
            )


            if (
                self._local_name(
                    root.tag
                )
                == "BibliographicResource"
            ):

                records.insert(
                    0,
                    root
                )


            # =================================================
            # 5. FALLBACK GÉNÉRIQUE
            # =================================================

            if not records:

                print(
                    "[FAO DATASET PARSER] "
                    "Recherche générique..."
                )

                for element in root.iter():

                    if (
                        self._local_name(
                            element.tag
                        )
                        == "BibliographicResource"
                    ):

                        records.append(
                            element
                        )


            print(
                "[FAO DATASET PARSER] "
                f"{len(records)} notice(s) trouvée(s)."
            )


            if not records:

                return []


            # =================================================
            # 6. PARCOURIR LES NOTICES
            # =================================================

            for index, record in enumerate(
                records,
                start=1
            ):

                try:

                    document = self._parse_record(
                        record=record,
                        namespaces=namespaces,
                        filename=filename,
                        source_url=source_url,
                        index=index
                    )

                    if document:

                        documents.append(
                            document
                        )


                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {index} ignorée : {e}"
                    )


            print("=" * 60)

            print(
                "[FAO DATASET PARSER] "
                f"{len(documents)} document(s) analysé(s)."
            )

            print("=" * 60)

            return documents


        except ET.ParseError as e:

            print(
                "[FAO DATASET PARSER] "
                f"Erreur XML : {e}"
            )

            return []


        except Exception as e:

            print(
                "[FAO DATASET PARSER] "
                f"Erreur parsing : {e}"
            )

            return []


    # =========================================================
    # PARSER UNE NOTICE AGRIS
    # =========================================================

    def _parse_record(
        self,
        record,
        namespaces,
        filename,
        source_url,
        index
    ):

        # =====================================================
        # TITRE
        # =====================================================

        title = self._get_text(
            record,
            [
                "dc:title",
                "dct:title",
            ],
            namespaces
        )

        if not title:

            title = (
                f"Document AGRIS {index}"
            )


        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = self._get_text(
            record,
            [
                "dc:description",
                "dct:description",
            ],
            namespaces
        )


        # =====================================================
        # AUTEURS
        # =====================================================

        authors = self._get_all_text(
            record,
            [
                "dc:creator",
                "dct:creator",
            ],
            namespaces
        )


        # =====================================================
        # DATE
        # =====================================================

        raw_date = self._get_text(
            record,
            [
                "dc:date",
                "dct:date",
                "dct:issued",
            ],
            namespaces
        )

        published_at = self._parse_date(
            raw_date
        )


        # =====================================================
        # TYPE DE PUBLICATION
        # =====================================================

        publication_type = self._get_text(
            record,
            [
                "dc:type",
                "dct:type",
            ],
            namespaces
        )


        # =====================================================
        # MOTS-CLÉS
        # =====================================================

        keywords = self._get_all_text(
            record,
            [
                "dc:subject",
                "dct:subject",
            ],
            namespaces
        )


        # =====================================================
        # SOURCE DE PUBLICATION
        # =====================================================

        publication_source = self._get_text(
            record,
            [
                "dc:source",
                "dct:source",
            ],
            namespaces
        )


        # =====================================================
        # ÉDITEUR
        # =====================================================

        publisher = self._get_text(
            record,
            [
                "dc:publisher",
                "dct:publisher",
            ],
            namespaces
        )


        # =====================================================
        # LANGUE
        # =====================================================

        language = self._get_text(
            record,
            [
                "dc:language",
                "dct:language",
            ],
            namespaces
        )

        language = self._normalize_language(
            language
        )


        # =====================================================
        # IDENTIFIANTS
        # =====================================================

        identifiers = self._get_all_text(
            record,
            [
                "dc:identifier",
                "dct:identifier",
            ],
            namespaces
        )


        # =====================================================
        # IDENTIFIANT AGRIS
        # =====================================================

        agris_id = self._get_agris_id(
            record,
            namespaces
        )

        if (
            not agris_id
            and identifiers
        ):

            for identifier in identifiers:

                if not identifier.startswith(
                    (
                        "http://",
                        "https://"
                    )
                ):

                    agris_id = identifier
                    break


        # =====================================================
        # URL DU DOCUMENT
        # =====================================================

        url = self._get_document_url(
            record,
            namespaces
        )


        if not url:

            if agris_id:

                url = (
                    "https://agris.fao.org/"
                    "search/en/providers/"
                    "122436/records/"
                    f"{agris_id}"
                )

            elif source_url:

                url = source_url

            else:

                url = (
                    "https://agris.fao.org/"
                )


        # =====================================================
        # LOCALISATION
        # =====================================================
        #
        # IMPORTANT :
        # Nous ne mettons PAS "Bénin" automatiquement.
        #
        # On conserve seulement une localisation lorsqu'elle
        # existe réellement dans les métadonnées AGRIS.
        # =====================================================

        geographic_values = self._get_all_text(
            record,
            [
                "dc:coverage",
                "dct:coverage",
                "dct:spatial",
            ],
            namespaces
        )

        zone_geographique = (
            geographic_values[0]
            if geographic_values
            else None
        )

        country = self._extract_country(
            geographic_values
        )


        # =====================================================
        # CULTURE
        # =====================================================
        #
        # Pour le moment nous ne déduisons pas automatiquement
        # une culture à partir du texte.
        #
        # Une mauvaise culture serait plus dangereuse qu'une
        # valeur absente.
        # =====================================================

        crop = None
        culture = None


        # =====================================================
        # CONSTRUIRE LE CONTENU RAG
        # =====================================================

        content_parts = []

        content_parts.append(
            f"Titre : {title}"
        )


        if description:

            content_parts.append(
                f"Description : {description}"
            )


        if authors:

            content_parts.append(
                "Auteur(s) : "
                + ", ".join(
                    authors
                )
            )


        if raw_date:

            content_parts.append(
                f"Date : {raw_date}"
            )


        if publication_type:

            content_parts.append(
                f"Type : {publication_type}"
            )


        if keywords:

            content_parts.append(
                "Mots-clés : "
                + ", ".join(
                    keywords
                )
            )


        if publication_source:

            content_parts.append(
                "Publication : "
                f"{publication_source}"
            )


        if publisher:

            content_parts.append(
                f"Éditeur : {publisher}"
            )


        if language:

            content_parts.append(
                f"Langue : {language}"
            )


        if zone_geographique:

            content_parts.append(
                "Zone géographique : "
                f"{zone_geographique}"
            )


        if country:

            content_parts.append(
                f"Pays : {country}"
            )


        if agris_id:

            content_parts.append(
                "Identifiant AGRIS : "
                f"{agris_id}"
            )


        if url:

            content_parts.append(
                f"URL : {url}"
            )


        if filename:

            content_parts.append(
                "Dataset AGRIS : "
                f"{filename}"
            )


        content = "\n\n".join(
            content_parts
        )


        # =====================================================
        # DONNÉES DOCUMENT
        # =====================================================

        document_data = {

            "title":
                title,

            "source":
                "FAO AGRIS",

            "url":
                url,

            "published_at":
                published_at,

            "language":
                language,

            "document_type":
                publication_type
                or "agricultural_publication",

            "content":
                content,

            "description":
                description,

            "crop":
                crop,

            "culture":
                culture,

            "keywords":
                keywords
                if keywords
                else None,

            "mots_cles":
                keywords
                if keywords
                else None,

            "country":
                country,

            "zone_geographique":
                zone_geographique,

            "author":
                (
                    ", ".join(authors)
                    if authors
                    else None
                ),

            "authors":
                authors
                if authors
                else None,

            "publisher":
                publisher,

            "dataset_filename":
                filename,

            "identifier":
                agris_id,

        }


        # =====================================================
        # NE GARDER QUE LES CHAMPS ACCEPTÉS
        # =====================================================

        document_fields = (
            DocumentMetadata.model_fields
        )


        filtered_data = {

            key: value

            for key, value
            in document_data.items()

            if (
                key in document_fields
                and value is not None
            )

        }


        # =====================================================
        # CRÉER LE DOCUMENT
        # =====================================================

        return DocumentMetadata(
            **filtered_data
        )


    # =========================================================
    # EXTRAIRE UN TEXTE
    # =========================================================

    def _get_text(
        self,
        element,
        paths,
        namespaces
    ):

        for path in paths:

            try:

                child = element.find(
                    path,
                    namespaces
                )

                if (
                    child is not None
                    and child.text
                    and child.text.strip()
                ):

                    return child.text.strip()

            except Exception:

                pass


        expected_names = {

            path.split(":")[-1].lower()

            for path in paths

        }


        for child in element.iter():

            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )

            if (
                local_name
                in expected_names
                and child.text
                and child.text.strip()
            ):

                return child.text.strip()


        return None


    # =========================================================
    # EXTRAIRE PLUSIEURS VALEURS
    # =========================================================

    def _get_all_text(
        self,
        element,
        paths,
        namespaces
    ):

        values = []

        expected_names = {

            path.split(":")[-1].lower()

            for path in paths

        }


        for child in element.iter():

            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )


            if (
                local_name
                not in expected_names
            ):

                continue


            if (
                child.text
                and child.text.strip()
            ):

                value = child.text.strip()

                if value not in values:

                    values.append(
                        value
                    )


        return values


    # =========================================================
    # IDENTIFIANT AGRIS
    # =========================================================

    def _get_agris_id(
        self,
        element,
        namespaces
    ):

        xml_id = element.attrib.get(
            "{http://www.w3.org/XML/1998/namespace}id"
        )

        if xml_id:

            return xml_id.strip()


        try:

            identifiers = element.findall(
                "dc:identifier",
                namespaces
            )

            for identifier in identifiers:

                identifier_type = (
                    identifier.attrib.get(
                        "type",
                        ""
                    )
                    .strip()
                    .lower()
                )

                if (
                    identifier_type == "agris"
                    and identifier.text
                    and identifier.text.strip()
                ):

                    return identifier.text.strip()

        except Exception:

            pass


        return None


    # =========================================================
    # URL DU DOCUMENT
    # =========================================================

    def _get_document_url(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # 1. IDENTIFIANTS DC
        # -----------------------------------------------------

        try:

            identifiers = element.findall(
                "dc:identifier",
                namespaces
            )

            # Priorité aux identifiants explicitement URL

            for identifier in identifiers:

                value = (
                    identifier.text.strip()
                    if (
                        identifier.text
                        and identifier.text.strip()
                    )
                    else None
                )

                if not value:

                    continue

                identifier_type = (
                    identifier.attrib.get(
                        "type",
                        ""
                    )
                    .strip()
                    .lower()
                )

                if (
                    identifier_type == "url"
                    and value.startswith(
                        (
                            "http://",
                            "https://"
                        )
                    )
                ):

                    return value


            # Ensuite n'importe quelle URL valide

            for identifier in identifiers:

                if (
                    identifier.text
                    and identifier.text.strip()
                ):

                    value = identifier.text.strip()

                    if value.startswith(
                        (
                            "http://",
                            "https://"
                        )
                    ):

                        return value

        except Exception:

            pass


        # -----------------------------------------------------
        # 2. IDENTIFIANTS DCT
        # -----------------------------------------------------

        try:

            identifiers = element.findall(
                "dct:identifier",
                namespaces
            )

            for identifier in identifiers:

                if (
                    identifier.text
                    and identifier.text.strip()
                ):

                    value = identifier.text.strip()

                    if value.startswith(
                        (
                            "http://",
                            "https://"
                        )
                    ):

                        return value

        except Exception:

            pass


        # -----------------------------------------------------
        # 3. FALLBACK GÉNÉRIQUE
        # -----------------------------------------------------

        for child in element.iter():

            if not (
                child.text
                and child.text.strip()
            ):

                continue


            value = child.text.strip()

            if not value.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                continue


            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )


            if local_name in [
                "identifier",
                "url",
                "landingpage",
                "accessurl",
            ]:

                return value


        return None


    # =========================================================
    # NORMALISER LA LANGUE
    # =========================================================

    def _normalize_language(
        self,
        language
    ):

        if not language:

            return None


        value = str(
            language
        ).strip()


        if not value:

            return None


        normalized = {
            "english": "en",
            "eng": "en",
            "en": "en",

            "french": "fr",
            "fra": "fr",
            "fre": "fr",
            "fr": "fr",

            "portuguese": "pt",
            "por": "pt",
            "pt": "pt",

            "spanish": "es",
            "spa": "es",
            "es": "es",
        }


        return normalized.get(
            value.lower(),
            value
        )


    # =========================================================
    # CONVERTIR UNE DATE
    # =========================================================

    def _parse_date(
        self,
        value
    ):

        if not value:

            return None


        value = str(
            value
        ).strip()


        # -----------------------------------------------------
        # YYYY-MM-DD
        # -----------------------------------------------------

        try:

            return date.fromisoformat(
                value[:10]
            )

        except Exception:

            pass


        # -----------------------------------------------------
        # ANNÉE SEULE : YYYY
        # -----------------------------------------------------

        match = re.search(
            r"\b(19|20)\d{2}\b",
            value
        )


        if match:

            try:

                return date(
                    int(
                        match.group(0)
                    ),
                    1,
                    1
                )

            except Exception:

                pass


        return None


    # =========================================================
    # EXTRAIRE LE PAYS
    # =========================================================

    def _extract_country(
        self,
        geographic_values
    ):

        if not geographic_values:

            return None


        # Pour l'instant, nous conservons uniquement
        # une valeur géographique explicite.
        #
        # Nous n'essayons PAS de deviner le pays depuis
        # le titre ou la description.

        if len(
            geographic_values
        ) == 1:

            value = str(
                geographic_values[0]
            ).strip()

            if value:

                return value


        return None


    # =========================================================
    # NOM LOCAL D'UN TAG XML
    # =========================================================

    def _local_name(
        self,
        tag
    ):

        if not isinstance(
            tag,
            str
        ):

            return ""


        if "}" in tag:

            return tag.split(
                "}",
                1
            )[1]


        if ":" in tag:

            return tag.split(
                ":",
                1
            )[1]


        return tag
