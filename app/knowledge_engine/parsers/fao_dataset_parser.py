import io
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS de la FAO.

        Le parser accepte :
        - bytes
        - str XML
        - flux avec .read()
        - fichier local via pathlib.Path
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


            # =================================================
            # 2. NAMESPACES
            # =================================================

            namespaces = {

                "rdf":
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",

                "dc":
                    "http://purl.org/dc/elements/1.1/",

                "dct":
                    "http://purl.org/dc/terms/",

                "dctypes":
                    "http://purl.org/dc/dcmitype/",

                "dcat":
                    "http://www.w3.org/ns/dcat#",

                "agr":
                    "http://purl.org/agris/",

            }


            # =================================================
            # 3. RECHERCHER LES NOTICES AGRIS
            # =================================================

            records = []


            # -------------------------------------------------
            # FORMAT AGRIS OBSERVÉ
            #
            # <dctypes:BibliographicResource>
            # -------------------------------------------------

            for element in root.iter():

                if not isinstance(
                    element.tag,
                    str
                ):

                    continue


                local_name = (
                    element.tag
                    .split("}")[-1]
                    .lower()
                )


                if local_name == (
                    "bibliographicresource"
                ):

                    records.append(
                        element
                    )


            # -------------------------------------------------
            # FALLBACK RDF Description
            # -------------------------------------------------

            if not records:

                records.extend(
                    root.findall(
                        ".//rdf:Description",
                        namespaces
                    )
                )


            # -------------------------------------------------
            # FALLBACK DCAT Dataset
            # -------------------------------------------------

            if not records:

                records.extend(
                    root.findall(
                        ".//dcat:Dataset",
                        namespaces
                    )
                )


            # -------------------------------------------------
            # ÉVITER LES DOUBLONS
            # -------------------------------------------------

            unique_records = []

            seen_ids = set()


            for record in records:

                record_id = id(
                    record
                )

                if record_id not in seen_ids:

                    seen_ids.add(
                        record_id
                    )

                    unique_records.append(
                        record
                    )


            records = unique_records


            print(
                "[FAO DATASET PARSER] "
                f"{len(records)} notice(s) trouvée(s)."
            )


            # =================================================
            # 4. PARCOURIR LES NOTICES
            # =================================================

            for record_index, record in enumerate(
                records,
                start=1
            ):

                try:

                    # =========================================
                    # TITRE
                    # =========================================

                    title = self._get_text(
                        record,
                        [
                            "dc:title",
                            "dct:title",
                            "title",
                        ],
                        namespaces
                    )


                    if not title:

                        title = (
                            "Document AGRIS"
                        )


                    # =========================================
                    # DESCRIPTION
                    # =========================================

                    description = self._get_text(
                        record,
                        [
                            "dc:description",
                            "dct:description",
                            "description",
                            "abstract",
                        ],
                        namespaces
                    )


                    # =========================================
                    # ABSTRACT
                    # =========================================

                    abstract = self._get_text(
                        record,
                        [
                            "agr:abstract",
                            "dc:abstract",
                            "dct:abstract",
                            "abstract",
                        ],
                        namespaces
                    )


                    # =========================================
                    # AUTEUR
                    # =========================================

                    authors = self._get_all_text(
                        record,
                        [
                            "dc:creator",
                            "dct:creator",
                            "creator",
                            "author",
                        ],
                        namespaces
                    )


                    author = None

                    if authors:

                        author = ", ".join(
                            authors
                        )


                    # =========================================
                    # ÉDITEUR
                    # =========================================

                    publisher = self._get_text(
                        record,
                        [
                            "dc:publisher",
                            "dct:publisher",
                            "publisher",
                        ],
                        namespaces
                    )


                    # =========================================
                    # LANGUE
                    # =========================================

                    language = self._get_text(
                        record,
                        [
                            "dc:language",
                            "dct:language",
                            "language",
                        ],
                        namespaces
                    )


                    # =========================================
                    # DATE
                    # =========================================

                    year = self._get_text(
                        record,
                        [
                            "dc:date",
                            "dct:date",
                            "date",
                            "year",
                        ],
                        namespaces
                    )


                    # =========================================
                    # MOTS-CLÉS
                    # =========================================

                    keywords = self._get_all_text(
                        record,
                        [
                            "dc:subject",
                            "dct:subject",
                            "subject",
                            "keyword",
                            "keywords",
                        ],
                        namespaces
                    )


                    # =========================================
                    # SOURCE
                    # =========================================

                    source = self._get_text(
                        record,
                        [
                            "dc:source",
                            "dct:source",
                            "source",
                        ],
                        namespaces
                    )


                    if not source:

                        source = (
                            "FAO AGRIS"
                        )


                    # =========================================
                    # IDENTIFIANT AGRIS
                    # =========================================

                    identifier = (
                        self._get_identifier(
                            record,
                            namespaces
                        )
                    )


                    # =========================================
                    # URL
                    # =========================================

                    url = self._get_url(
                        record,
                        namespaces
                    )


                    # =========================================
                    # URL DE SECOURS
                    # =========================================

                    if not url:

                        if identifier:

                            if identifier.startswith(
                                (
                                    "http://",
                                    "https://"
                                )
                            ):

                                url = identifier

                            else:

                                url = (
                                    "https://agris.fao.org/"
                                    "search/en/providers/"
                                    "122436/records/"
                                    f"{identifier}"
                                )


                        elif source_url:

                            url = str(
                                source_url
                            ).strip()


                        else:

                            url = (
                                "https://agris.fao.org/"
                            )


                    # =========================================
                    # CONSTRUIRE LE CONTENU RAG
                    # =========================================

                    content_parts = []


                    content_parts.append(
                        f"Titre : {title}"
                    )


                    if description:

                        content_parts.append(
                            f"Description : "
                            f"{description}"
                        )


                    if abstract:

                        # Éviter de dupliquer
                        # exactement la description

                        if abstract != description:

                            content_parts.append(
                                f"Résumé : "
                                f"{abstract}"
                            )


                    if author:

                        content_parts.append(
                            f"Auteur : "
                            f"{author}"
                        )


                    if publisher:

                        content_parts.append(
                            f"Éditeur : "
                            f"{publisher}"
                        )


                    if language:

                        content_parts.append(
                            f"Langue : "
                            f"{language}"
                        )


                    if year:

                        content_parts.append(
                            f"Année : "
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
                            f"Source : "
                            f"{source}"
                        )


                    if identifier:

                        content_parts.append(
                            f"Identifiant AGRIS : "
                            f"{identifier}"
                        )


                    if url:

                        content_parts.append(
                            f"URL : "
                            f"{url}"
                        )


                    if filename:

                        content_parts.append(
                            f"Dataset FAO : "
                            f"{filename}"
                        )


                    content = "\n\n".join(
                        content_parts
                    )


                    # =========================================
                    # DONNÉES DU DOCUMENT
                    # =========================================

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

                        "identifier":
                            identifier,

                    }


                    # =========================================
                    # FILTRER SELON DOCUMENTMETADATA
                    # =========================================

                    document_fields = (
                        DocumentMetadata
                        .model_fields
                    )


                    filtered_data = {

                        key: value

                        for key, value
                        in document_data.items()

                        if key
                        in document_fields

                    }


                    # =========================================
                    # CRÉER DOCUMENT PYDANTIC
                    # =========================================

                    document = (
                        DocumentMetadata(
                            **filtered_data
                        )
                    )


                    documents.append(
                        document
                    )


                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {record_index} ignorée : "
                        f"{e}"
                    )


            # =================================================
            # 5. RÉSULTAT FINAL
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

            # Si le contenu commence par <
            # c'est du XML direct

            if xml_content.lstrip().startswith(
                "<"
            ):

                return ET.fromstring(
                    xml_content
                )


            # Sinon on considère que c'est
            # un chemin vers un fichier

            tree = ET.parse(
                xml_content
            )

            return tree.getroot()


        # -----------------------------------------------------
        # PATHLIB
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
            "Utilisez bytes, str, pathlib.Path "
            "ou un flux."
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

            expected_name = (
                path
                .split(":")[-1]
                .lower()
            )


            # -------------------------------------------------
            # RECHERCHE DIRECTE AVEC NAMESPACE
            # -------------------------------------------------

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

                    return (
                        child.text.strip()
                    )


            except Exception:

                pass


            # -------------------------------------------------
            # RECHERCHE GÉNÉRIQUE
            # -------------------------------------------------

            for child in element.iter():

                if not isinstance(
                    child.tag,
                    str
                ):

                    continue


                local_name = (
                    child.tag
                    .split("}")[-1]
                    .lower()
                )


                if (
                    local_name
                    == expected_name
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
        paths,
        namespaces
    ):

        values = []


        expected_names = {

            path
            .split(":")[-1]
            .lower()

            for path in paths

        }


        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue


            local_name = (
                child.tag
                .split("}")[-1]
                .lower()
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
    # EXTRAIRE IDENTIFIANT
    # =========================================================

    def _get_identifier(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # CHERCHER TOUS LES IDENTIFIANTS
        # -----------------------------------------------------

        identifiers = []


        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue


            local_name = (
                child.tag
                .split("}")[-1]
                .lower()
            )


            if local_name != (
                "identifier"
            ):

                continue


            if not child.text:

                continue


            value = (
                child.text.strip()
            )


            if not value:

                continue


            # Ignorer les URLs ici.
            # On les traite dans _get_url.

            if value.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                continue


            if value not in identifiers:

                identifiers.append(
                    value
                )


        if identifiers:

            return identifiers[0]


        return None


    # =========================================================
    # EXTRAIRE URL
    # =========================================================

    def _get_url(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # CHERCHER LES IDENTIFIANTS URL
        # -----------------------------------------------------

        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue


            local_name = (
                child.tag
                .split("}")[-1]
                .lower()
            )


            if local_name not in [

                "identifier",

                "url",

                "landingpage",

                "accessurl",

            ]:

                continue


            if not child.text:

                continue


            value = (
                child.text.strip()
            )


            if value.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return value


        return None
