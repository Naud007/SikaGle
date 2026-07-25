import io
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS de la FAO.

        Le parser accepte :
        - bytes
        - str
        - fichier Path
        - flux contenant du XML

        Le XML AGRIS contient notamment des éléments :
        dctypes:BibliographicResource
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

        print(
            "[FAO DATASET PARSER] "
            f"Analyse du dataset : "
            f"{filename or 'dataset XML'}"
        )

        documents = []

        try:

            # =================================================
            # 1. CHARGER LE XML
            # =================================================

            root = self._load_xml(
                xml_content
            )

            if root is None:

                print(
                    "[FAO DATASET PARSER] "
                    "Impossible de charger le XML."
                )

                return []


            print(
                "[FAO DATASET PARSER] "
                "Root XML :",
                root.tag
            )


            # =================================================
            # 2. RECHERCHER LES NOTICES AGRIS
            # =================================================

            records = []


            for element in root.iter():

                if not isinstance(
                    element.tag,
                    str
                ):

                    continue


                local_name = (
                    self._local_name(
                        element.tag
                    )
                )


                # -------------------------------------------------
                # STRUCTURE RÉELLE AGRIS
                # -------------------------------------------------

                if local_name == (
                    "bibliographicresource"
                ):

                    records.append(
                        element
                    )


            print(
                "[FAO DATASET PARSER] "
                f"{len(records)} "
                "notice(s) BibliographicResource trouvée(s)."
            )


            # =================================================
            # FALLBACK
            # =================================================

            if not records:

                print(
                    "[FAO DATASET PARSER] "
                    "Aucune BibliographicResource trouvée."
                )

                # ---------------------------------------------
                # Recherche rdf:Description
                # ---------------------------------------------

                for element in root.iter():

                    if not isinstance(
                        element.tag,
                        str
                    ):

                        continue


                    local_name = (
                        self._local_name(
                            element.tag
                        )
                    )


                    if local_name == (
                        "description"
                    ):

                        records.append(
                            element
                        )


                print(
                    "[FAO DATASET PARSER] "
                    f"Fallback rdf:Description : "
                    f"{len(records)} notice(s)."
                )


            # =================================================
            # 3. PARCOURIR LES NOTICES
            # =================================================

            for index, record in enumerate(
                records,
                start=1
            ):

                try:

                    document = (
                        self._parse_record(
                            record=record,
                            filename=filename,
                            source_url=source_url
                        )
                    )


                    if document is not None:

                        documents.append(
                            document
                        )


                    # -----------------------------------------
                    # LOG PROGRESSIF
                    # -----------------------------------------

                    if (
                        index <= 3
                        or index % 1000 == 0
                    ):

                        print(
                            "[FAO DATASET PARSER] "
                            f"Notice {index} "
                            f"/ {len(records)} "
                            "traitée."
                        )


                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {index} ignorée : "
                        f"{e}"
                    )


            # =================================================
            # 4. RÉSULTAT
            # =================================================

            print(
                "[FAO DATASET PARSER] "
                f"{len(documents)} document(s) "
                "analysé(s)."
            )


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
    # CHARGER LE XML
    # =========================================================

    def _load_xml(
        self,
        xml_content
    ):

        # -----------------------------------------------------
        # BYTES
        # -----------------------------------------------------

        if isinstance(
            xml_content,
            bytes
        ):

            xml_stream = io.BytesIO(
                xml_content
            )

            tree = ET.parse(
                xml_stream
            )

            return tree.getroot()


        # -----------------------------------------------------
        # STRING
        # -----------------------------------------------------

        if isinstance(
            xml_content,
            str
        ):

            # ---------------------------------------------
            # Si la chaîne ressemble à un chemin
            # ---------------------------------------------

            if (
                len(
                    xml_content
                ) < 500
                and (
                    xml_content.endswith(
                        ".xml"
                    )
                    or
                    xml_content.startswith(
                        "/"
                    )
                )
            ):

                tree = ET.parse(
                    xml_content
                )

                return tree.getroot()


            # ---------------------------------------------
            # Sinon XML texte
            # ---------------------------------------------

            return ET.fromstring(
                xml_content
            )


        # -----------------------------------------------------
        # PATH OU OBJET COMPATIBLE AVEC open()
        # -----------------------------------------------------

        if hasattr(
            xml_content,
            "__fspath__"
        ):

            tree = ET.parse(
                xml_content
            )

            return tree.getroot()


        # -----------------------------------------------------
        # FLUX
        # -----------------------------------------------------

        if hasattr(
            xml_content,
            "read"
        ):

            tree = ET.parse(
                xml_content
            )

            return tree.getroot()


        # -----------------------------------------------------
        # FORMAT INCONNU
        # -----------------------------------------------------

        raise ValueError(
            "Format XML non supporté. "
            "Utilisez bytes, str, Path ou un flux."
        )


    # =========================================================
    # PARSER UNE NOTICE AGRIS
    # =========================================================

    def _parse_record(
        self,
        record,
        filename=None,
        source_url=None
    ):

        # =====================================================
        # TITRE
        # =====================================================

        title = self._get_text(
            record,
            [
                "title",
            ]
        )


        if not title:

            title = (
                "Document AGRIS"
            )


        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = self._get_text(
            record,
            [
                "description",
                "abstract",
            ]
        )


        # =====================================================
        # ABSTRACT
        # =====================================================

        abstract = self._get_text(
            record,
            [
                "abstract",
            ]
        )


        # =====================================================
        # AUTEUR
        # =====================================================

        authors = self._get_all_text(
            record,
            [
                "creator",
                "author",
            ]
        )


        author = None

        if authors:

            author = "; ".join(
                authors
            )


        # =====================================================
        # ÉDITEUR
        # =====================================================

        publisher = self._get_text(
            record,
            [
                "publisher",
            ]
        )


        # =====================================================
        # LANGUE
        # =====================================================

        language = self._get_text(
            record,
            [
                "language",
            ]
        )


        # =====================================================
        # DATE
        # =====================================================

        year = self._get_text(
            record,
            [
                "date",
                "issued",
                "created",
            ]
        )


        # =====================================================
        # MOTS-CLÉS
        # =====================================================

        keywords = self._get_all_text(
            record,
            [
                "subject",
                "keyword",
                "keywords",
            ]
        )


        # =====================================================
        # SOURCE
        # =====================================================

        source = self._get_text(
            record,
            [
                "source",
            ]
        )


        if not source:

            source = (
                "FAO AGRIS"
            )


        # =====================================================
        # IDENTIFIANT
        # =====================================================

        identifiers = self._get_all_text(
            record,
            [
                "identifier",
            ]
        )


        # =====================================================
        # URL
        # =====================================================

        url = self._extract_url(
            record
        )


        # =====================================================
        # URL DE SECOURS
        # =====================================================

        if not url:

            # ---------------------------------------------
            # Chercher un identifiant URL
            # ---------------------------------------------

            for identifier in identifiers:

                if identifier.startswith(
                    (
                        "http://",
                        "https://"
                    )
                ):

                    url = identifier

                    break


        # ---------------------------------------------
        # Identifiant AGRIS
        # ---------------------------------------------

        if not url:

            agris_identifier = (
                self._get_attribute_identifier(
                    record
                )
            )


            if agris_identifier:

                url = (
                    "https://agris.fao.org/"
                    "search/en/providers/"
                    "122436/records/"
                    f"{agris_identifier}"
                )


        # ---------------------------------------------
        # URL dataset
        # ---------------------------------------------

        if not url:

            if source_url:

                url = source_url

            else:

                url = (
                    "https://agris.fao.org/"
                )


        # =====================================================
        # CONSTRUIRE LE CONTENU RAG
        # =====================================================

        content_parts = []


        content_parts.append(
            f"Titre : {title}"
        )


        if description:

            content_parts.append(
                "Description : "
                f"{description}"
            )


        if abstract:

            # Éviter de répéter exactement
            # la description

            if abstract != description:

                content_parts.append(
                    "Résumé : "
                    f"{abstract}"
                )


        if author:

            content_parts.append(
                "Auteur : "
                f"{author}"
            )


        if publisher:

            content_parts.append(
                "Éditeur : "
                f"{publisher}"
            )


        if language:

            content_parts.append(
                "Langue : "
                f"{language}"
            )


        if year:

            content_parts.append(
                "Année : "
                f"{year}"
            )


        if keywords:

            content_parts.append(
                "Mots-clés : "
                + ", ".join(
                    keywords
                )
            )


        if source:

            content_parts.append(
                "Source : "
                f"{source}"
            )


        if url:

            content_parts.append(
                "URL : "
                f"{url}"
            )


        if filename:

            content_parts.append(
                "Dataset FAO : "
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

            "url":
                url,

            "description":
                description,

            "source":
                source,

            "content":
                content,

            "language":
                language,

            "year":
                year,

            "keywords":
                keywords,

            "author":
                author,

            "publisher":
                publisher,

            "dataset_filename":
                filename,

        }


        # =====================================================
        # FILTRER SELON DocumentMetadata
        # =====================================================

        document_fields = (
            DocumentMetadata
            .model_fields
        )


        filtered_data = {

            key:
                value

            for key, value
            in document_data.items()

            if key
            in document_fields

        }


        # =====================================================
        # CRÉER LE DOCUMENT
        # =====================================================

        document = (
            DocumentMetadata(
                **filtered_data
            )
        )


        return document


    # =========================================================
    # EXTRAIRE UN TEXTE
    # =========================================================

    def _get_text(
        self,
        element,
        names
    ):

        expected_names = {

            name
            .split(":")[-1]
            .lower()

            for name
            in names

        }


        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue


            local_name = (
                self._local_name(
                    child.tag
                )
            )


            if (
                local_name
                in expected_names
            ):

                if (
                    child.text
                    and child.text.strip()
                ):

                    return (
                        child.text.strip()
                    )


        return None


    # =========================================================
    # EXTRAIRE PLUSIEURS TEXTES
    # =========================================================

    def _get_all_text(
        self,
        element,
        names
    ):

        values = []


        expected_names = {

            name
            .split(":")[-1]
            .lower()

            for name
            in names

        }


        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue


            local_name = (
                self._local_name(
                    child.tag
                )
            )


            if (
                local_name
                in expected_names
            ):

                if (
                    child.text
                    and child.text.strip()
                ):

                    value = (
                        child.text.strip()
                    )


                    if value not in values:

                        values.append(
                            value
                        )


        return values


    # =========================================================
    # EXTRAIRE URL
    # =========================================================

    def _extract_url(
        self,
        element
    ):

        # -----------------------------------------------------
        # 1. IDENTIFIERS
        # -----------------------------------------------------

        identifiers = self._get_all_text(
            element,
            [
                "identifier",
            ]
        )


        for identifier in identifiers:

            identifier = (
                identifier.strip()
            )


            if identifier.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return identifier


        # -----------------------------------------------------
        # 2. LANDING PAGE
        # -----------------------------------------------------

        landing_page = self._get_text(
            element,
            [
                "landingPage",
            ]
        )


        if landing_page:

            landing_page = (
                landing_page.strip()
            )


            if landing_page.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return landing_page


        # -----------------------------------------------------
        # 3. ACCESS URL
        # -----------------------------------------------------

        access_url = self._get_text(
            element,
            [
                "accessURL",
            ]
        )


        if access_url:

            access_url = (
                access_url.strip()
            )


            if access_url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return access_url


        # -----------------------------------------------------
        # 4. RECHERCHE DANS LES ATTRIBUTS
        # -----------------------------------------------------

        for child in element.iter():

            for attribute_value in (
                child.attrib.values()
            ):

                if not isinstance(
                    attribute_value,
                    str
                ):

                    continue


                attribute_value = (
                    attribute_value.strip()
                )


                if attribute_value.startswith(
                    (
                        "http://",
                        "https://"
                    )
                ):

                    return attribute_value


        return None


    # =========================================================
    # EXTRAIRE IDENTIFIANT AGRIS DEPUIS XML:ID
    # =========================================================

    def _get_attribute_identifier(
        self,
        element
    ):

        # -----------------------------------------------------
        # Chercher xml:id
        # -----------------------------------------------------

        for attribute_name, attribute_value in (
            element.attrib.items()
        ):

            if not isinstance(
                attribute_value,
                str
            ):

                continue


            local_name = (
                attribute_name
                .split("}")[-1]
                .lower()
            )


            if local_name == "id":

                return (
                    attribute_value.strip()
                )


        return None


    # =========================================================
    # EXTRAIRE NOM LOCAL XML
    # =========================================================

    def _local_name(
        self,
        tag
    ):

        if "}" in tag:

            return (
                tag.split(
                    "}"
                )[-1]
                .lower()
            )


        return (
            tag
            .split(":")[-1]
            .lower()
        )
