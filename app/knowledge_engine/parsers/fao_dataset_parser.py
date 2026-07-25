import io
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS de la FAO.

        Le parser fonctionne directement avec le contenu XML
        en mémoire. Aucun fichier local n'est nécessaire.
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

            # -------------------------------------------------
            # 1. CHARGER LE XML
            # -------------------------------------------------

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

            elif isinstance(
                xml_content,
                str
            ):

                # Le contenu est un XML texte
                root = ET.fromstring(
                    xml_content
                )

                tree = ET.ElementTree(
                    root
                )

            elif hasattr(
                xml_content,
                "read"
            ):

                tree = ET.parse(
                    xml_content
                )

            else:

                raise ValueError(
                    "Format XML non supporté. "
                    "Utilisez bytes, str ou un flux."
                )


            root = tree.getroot()


            # -------------------------------------------------
            # 2. NAMESPACES
            # -------------------------------------------------

            namespaces = {

                "rdf":
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",

                "dc":
                    "http://purl.org/dc/elements/1.1/",

                "dct":
                    "http://purl.org/dc/terms/",

                "dcat":
                    "http://www.w3.org/ns/dcat#",

                "agr":
                    "http://purl.org/agris/",

            }


            # -------------------------------------------------
            # 3. RECHERCHE DES NOTICES
            # -------------------------------------------------

            records = []


            # RDF Description
            records.extend(
                root.findall(
                    ".//rdf:Description",
                    namespaces
                )
            )


            # DCAT Dataset
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


            # -------------------------------------------------
            # FALLBACK
            # -------------------------------------------------

            if not records:

                for element in root.iter():

                    title = self._get_text(
                        element,
                        [
                            "dc:title",
                            "dct:title",
                            "title",
                        ],
                        namespaces
                    )

                    if title:

                        records.append(
                            element
                        )


            print(
                "[FAO DATASET PARSER] "
                f"{len(records)} notice(s) trouvée(s)."
            )


            # -------------------------------------------------
            # 4. PARCOURIR LES NOTICES
            # -------------------------------------------------

            for record in records:

                try:

                    # -----------------------------------------
                    # TITRE
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # DESCRIPTION
                    # -----------------------------------------

                    description = self._get_text(
                        record,
                        [
                            "dc:description",
                            "dct:description",
                            "description",
                            "abstract",
                            "agr:abstract",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # RÉSUMÉ / ABSTRACT
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # AUTEUR
                    # -----------------------------------------

                    author = self._get_text(
                        record,
                        [
                            "dc:creator",
                            "dct:creator",
                            "creator",
                            "author",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # ÉDITEUR
                    # -----------------------------------------

                    publisher = self._get_text(
                        record,
                        [
                            "dc:publisher",
                            "dct:publisher",
                            "publisher",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # LANGUE
                    # -----------------------------------------

                    language = self._get_text(
                        record,
                        [
                            "dc:language",
                            "dct:language",
                            "language",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # DATE / ANNÉE
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # MOTS-CLÉS
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # SOURCE
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # IDENTIFIANT
                    # -----------------------------------------

                    identifier = self._get_text(
                        record,
                        [
                            "dc:identifier",
                            "dct:identifier",
                            "identifier",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # URL
                    # -----------------------------------------

                    url = self._get_url(
                        record,
                        namespaces
                    )


                    # -----------------------------------------
                    # URL DE SECOURS
                    # -----------------------------------------

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

                            url = source_url

                        else:

                            url = (
                                "https://agris.fao.org/"
                            )


                    # -----------------------------------------
                    # CONSTRUIRE LE CONTENU RAG
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # DOCUMENT
                    # -----------------------------------------

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


                    # Ajouter uniquement les champs
                    # acceptés par DocumentMetadata

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
                        f"Notice ignorée : {e}"
                    )


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
    # EXTRAIRE UN TEXTE
    # =========================================================

    def _get_text(
        self,
        element,
        paths,
        namespaces
    ):

        for path in paths:

            # -------------------------------------------------
            # RECHERCHE AVEC NAMESPACE
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


                expected_name = (
                    path
                    .split(":")[-1]
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
    # EXTRAIRE URL
    # =========================================================

    def _get_url(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # 1. IDENTIFIER
        # -----------------------------------------------------

        identifier = self._get_text(
            element,
            [
                "dc:identifier",
                "dct:identifier",
                "identifier",
            ],
            namespaces
        )


        if identifier:

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

        landing_page = (
            element.find(
                "dcat:landingPage",
                namespaces
            )
        )


        if (
            landing_page is not None
            and landing_page.text
        ):

            url = (
                landing_page.text.strip()
            )


            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return url


        # -----------------------------------------------------
        # 3. ACCESS URL
        # -----------------------------------------------------

        access_url = (
            element.find(
                "dcat:accessURL",
                namespaces
            )
        )


        if (
            access_url is not None
            and access_url.text
        ):

            url = (
                access_url.text.strip()
            )


            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return url


        # -----------------------------------------------------
        # 4. RECHERCHE GÉNÉRIQUE
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


            if local_name in [

                "identifier",

                "url",

                "landingpage",

                "accessurl",

            ]:

                if (
                    child.text
                    and child.text.strip()
                ):

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
