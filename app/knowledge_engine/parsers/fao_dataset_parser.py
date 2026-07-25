import io
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS de la FAO.

        Les datasets AGRIS contiennent des notices
        de type dctypes:BibliographicResource.

        Le parser accepte :
        - bytes
        - str XML
        - flux fichier avec .read()
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


            # =================================================
            # 2. NAMESPACES AGRIS
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

                "agr":
                    "http://purl.org/agris/",

            }


            # =================================================
            # 3. RECHERCHER LES NOTICES AGRIS
            # =================================================

            records = root.findall(
                ".//dctypes:BibliographicResource",
                namespaces
            )


            print(
                "[FAO DATASET PARSER] "
                f"{len(records)} notice(s) "
                "BibliographicResource trouvée(s)."
            )


            # =================================================
            # 4. FALLBACK GÉNÉRIQUE
            # =================================================

            if not records:

                print(
                    "[FAO DATASET PARSER] "
                    "Aucune notice BibliographicResource. "
                    "Recherche générique..."
                )

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


                    if local_name in (
                        "bibliographicresource",
                        "description",
                        "record"
                    ):

                        records.append(
                            element
                        )


            # =================================================
            # 5. ÉVITER LES DOUBLONS
            # =================================================

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
                f"{len(records)} notice(s) "
                "à analyser."
            )


            # =================================================
            # 6. PARCOURIR LES NOTICES
            # =================================================

            for index, record in enumerate(
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
                    # DATE / ANNÉE
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

                    agris_identifier = (
                        self._get_identifier_by_type(
                            record,
                            "AGRIS",
                            namespaces
                        )
                    )


                    # =========================================
                    # IDENTIFIANT URL
                    # =========================================

                    url_identifier = (
                        self._get_identifier_by_type(
                            record,
                            "url",
                            namespaces
                        )
                    )


                    # =========================================
                    # URL
                    # =========================================

                    url = (
                        url_identifier
                    )


                    # =========================================
                    # FALLBACK URL AVEC IDENTIFIANT AGRIS
                    # =========================================

                    if not url:

                        if agris_identifier:

                            url = (
                                "https://agris.fao.org/"
                                "search/en/providers/"
                                "122436/records/"
                                f"{agris_identifier}"
                            )


                    # =========================================
                    # FALLBACK URL SOURCE DATASET
                    # =========================================

                    if not url:

                        if source_url:

                            url = (
                                str(
                                    source_url
                                ).strip()
                            )


                    # =========================================
                    # DERNIER FALLBACK
                    # =========================================

                    if not url:

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
                            "Description : "
                            f"{description}"
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


                    if agris_identifier:

                        content_parts.append(
                            "Identifiant AGRIS : "
                            f"{agris_identifier}"
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


                    content = (
                        "\n\n".join(
                            content_parts
                        )
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

                    }


                    # =========================================
                    # FILTRER LES CHAMPS ACCEPTÉS
                    # PAR DocumentMetadata
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
                    # CRÉER LE DOCUMENT
                    # =========================================

                    document = (
                        DocumentMetadata(
                            **filtered_data
                        )
                    )


                    documents.append(
                        document
                    )


                    # =========================================
                    # LOG
                    # =========================================

                    if index <= 3:

                        print(
                            f"[FAO DATASET PARSER] "
                            f"Document {index} : "
                            f"{title[:100]}"
                        )


                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {index} ignorée : "
                        f"{e}"
                    )


            # =================================================
            # 7. RÉSULTAT
            # =================================================

            print(
                "[FAO DATASET PARSER] "
                f"{len(documents)} document(s) "
                "analysé(s) avec succès."
            )


            return documents


        # =====================================================
        # ERREUR XML
        # =====================================================

        except ET.ParseError as e:

            print(
                "[FAO DATASET PARSER] "
                f"Erreur XML : {e}"
            )

            return []


        # =====================================================
        # ERREUR GÉNÉRALE
        # =====================================================

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

            expected_name = (
                path
                .split(":")[-1]
                .lower()
            )


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
    # EXTRAIRE UN IDENTIFIANT PAR TYPE
    # =========================================================

    def _get_identifier_by_type(
        self,
        element,
        identifier_type,
        namespaces
    ):

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


            if local_name != "identifier":

                continue


            child_type = (
                child.attrib
                .get(
                    "type"
                )
            )


            if not child_type:

                continue


            if (
                child_type.lower()
                != identifier_type.lower()
            ):

                continue


            if (
                child.text
                and child.text.strip()
            ):

                return (
                    child.text.strip()
                )


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
        # 1. IDENTIFIER TYPE URL
        # -----------------------------------------------------

        url = (
            self._get_identifier_by_type(
                element,
                "url",
                namespaces
            )
        )


        if url:

            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return url


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

            value = (
                landing_page.text.strip()
            )


            if value.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return value


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

            value = (
                access_url.text.strip()
            )


            if value.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                return value


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
def debug_fao_dataset(xml_path):

    import xml.etree.ElementTree as ET

    print("=" * 60)
    print("[DEBUG FAO] Analyse du fichier XML")
    print("=" * 60)

    print(
        "[DEBUG FAO] Fichier :",
        xml_path
    )

    try:

        tree = ET.parse(
            xml_path
        )

        root = tree.getroot()

        print(
            "[DEBUG FAO] Root tag :",
            root.tag
        )

        print(
            "[DEBUG FAO] Root attrib :",
            root.attrib
        )

        print("=" * 60)
        print("[DEBUG FAO] Enfants directs du root")
        print("=" * 60)

        for index, child in enumerate(
            list(root)[:20],
            start=1
        ):

            print(
                f"{index}.",
                child.tag,
                child.attrib
            )

        print("=" * 60)
        print("[DEBUG FAO] Recherche BibliographicResource")
        print("=" * 60)

        count = 0

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

            if local_name == "bibliographicresource":

                count += 1

                print(
                    f"[DEBUG FAO] "
                    f"BibliographicResource #{count}"
                )

                print(
                    "TAG :",
                    element.tag
                )

                print(
                    "ATTRIB :",
                    element.attrib
                )

                for child in list(element)[:10]:

                    print(
                        "  CHILD :",
                        child.tag,
                        "=",
                        child.text
                    )

                print("-" * 60)

        print(
            "[DEBUG FAO] "
            f"Total BibliographicResource : {count}"
        )

        print("=" * 60)

        return {
            "status": "success",
            "root": root.tag,
            "bibliographic_resources": count
        }

    except Exception as e:

        print(
            "[DEBUG FAO] "
            f"Erreur : {e}"
        )

        return {
            "status": "error",
            "message": str(e)
        }
