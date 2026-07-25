import io
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS de la FAO.

        Le parser accepte :
        - bytes
        - str contenant du XML
        - flux fichier
        - fichier local Path / str

        Le XML AGRIS réel utilise notamment :
        <dctypes:Dataset>
            <dctypes:BibliographicResource>
                <dc:title>...</dc:title>
                <dc:description>...</dc:description>
                ...
            </dctypes:BibliographicResource>
        </dctypes:Dataset>
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

            root = self._load_xml(
                xml_content
            )

            if root is None:

                print(
                    "[FAO DATASET PARSER] "
                    "Impossible de charger le XML."
                )

                return []


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

                "dctypes":
                    "http://purl.org/dc/dcmitype/",

                "dcat":
                    "http://www.w3.org/ns/dcat#",

                "agr":
                    "http://purl.org/agris/",
            }


            # -------------------------------------------------
            # 3. RECHERCHE DES VRAIES NOTICES AGRIS
            # -------------------------------------------------

            records = []


            # -------------------------------------------------
            # CAS PRINCIPAL AGRIS :
            #
            # <dctypes:BibliographicResource>
            # -------------------------------------------------

            records.extend(

                root.findall(

                    ".//dctypes:BibliographicResource",

                    namespaces

                )

            )


            # -------------------------------------------------
            # CAS RDF
            # -------------------------------------------------

            records.extend(

                root.findall(

                    ".//rdf:Description",

                    namespaces

                )

            )


            # -------------------------------------------------
            # CAS DCAT DATASET
            # -------------------------------------------------

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
            # FALLBACK :
            # RECHERCHER LES ÉLÉMENTS
            # BibliographicResource PAR NOM LOCAL
            # -------------------------------------------------

            if not records:

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


                    if (
                        local_name
                        == "bibliographicresource"
                    ):

                        records.append(
                            element
                        )


            # -------------------------------------------------
            # FALLBACK FINAL :
            # SI LE DOCUMENT XML EST LUI-MÊME UNE NOTICE
            # -------------------------------------------------

            if not records:

                title = self._get_text(

                    root,

                    [
                        "dc:title",
                        "dct:title",
                        "title",
                    ],

                    namespaces

                )

                if title:

                    records.append(
                        root
                    )


            print(

                "[FAO DATASET PARSER] "

                f"{len(records)} "
                "notice(s) trouvée(s)."

            )


            # -------------------------------------------------
            # 4. PARCOURIR LES NOTICES
            # -------------------------------------------------

            for index, record in enumerate(

                records,

                start=1

            ):

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
                    # ABSTRACT
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
                    # IDENTIFIANT AGRIS
                    # -----------------------------------------

                    identifier = (

                        self._get_identifier(

                            record,

                            namespaces

                        )

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

                            "Description : "
                            f"{description}"

                        )


                    if abstract:

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


                    if identifier:

                        content_parts.append(

                            "Identifiant AGRIS : "
                            f"{identifier}"

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


                    # -----------------------------------------
                    # DONNÉES DOCUMENT
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


                    # -----------------------------------------
                    # FILTRER LES CHAMPS PYDANTIC
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # CRÉER DOCUMENT
                    # -----------------------------------------

                    document = (

                        DocumentMetadata(

                            **filtered_data

                        )

                    )


                    documents.append(

                        document

                    )


                    # -----------------------------------------
                    # LOG
                    # -----------------------------------------

                    if index <= 3:

                        print(

                            "[FAO DATASET PARSER] "

                            f"Document {index} : "

                            f"{title[:100]}"

                        )


                except Exception as e:

                    print(

                        "[FAO DATASET PARSER] "

                        f"Notice {index} ignorée : "

                        f"{e}"

                    )


            # -------------------------------------------------
            # RÉSULTAT
            # -------------------------------------------------

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

            return ET.fromstring(

                xml_content

            )


        # -----------------------------------------------------
        # STRING
        # -----------------------------------------------------

        if isinstance(

            xml_content,

            str

        ):

            stripped = (

                xml_content.strip()

            )


            # XML directement
            if stripped.startswith(

                "<"

            ):

                return ET.fromstring(

                    xml_content

                )


            # Sinon considérer comme chemin fichier
            return ET.parse(

                xml_content

            ).getroot()


        # -----------------------------------------------------
        # PATHLIB
        # -----------------------------------------------------

        if hasattr(

            xml_content,

            "__fspath__"

        ):

            return ET.parse(

                xml_content

            ).getroot()


        # -----------------------------------------------------
        # FLUX
        # -----------------------------------------------------

        if hasattr(

            xml_content,

            "read"

        ):

            return ET.parse(

                xml_content

            ).getroot()


        # -----------------------------------------------------
        # OBJET RESPONSE / DICT
        # -----------------------------------------------------

        if isinstance(

            xml_content,

            dict

        ):

            content = (

                xml_content.get(

                    "content"

                )

            )


            if content:

                return self._load_xml(

                    content

                )


        # -----------------------------------------------------
        # FORMAT INCONNU
        # -----------------------------------------------------

        raise ValueError(

            "Format XML non supporté. "

            "Utilisez bytes, str, Path, "
            "flux ou dictionnaire contenant "
            "la clé 'content'."

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
    # EXTRAIRE IDENTIFIANT
    # =========================================================

    def _get_identifier(

        self,

        element,

        namespaces

    ):

        # -----------------------------------------------------
        # RECHERCHE DE TOUS LES IDENTIFIANTS
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


            if local_name != "identifier":

                continue


            if not child.text:

                continue


            value = (

                child.text.strip()

            )


            if not value:

                continue


            # Si URL, on la laisse à _get_url
            if value.startswith(

                (
                    "http://",
                    "https://"
                )

            ):

                continue


            # Priorité à l'identifiant AGRIS
            identifier_type = (

                child.attrib.get(

                    "type",

                    ""

                )

                .lower()

            )


            if identifier_type == "agris":

                return value


        # -----------------------------------------------------
        # FALLBACK IDENTIFIANT
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


            if local_name != "identifier":

                continue


            if not child.text:

                continue


            value = (

                child.text.strip()

            )


            if (

                value

                and not value.startswith(

                    (
                        "http://",
                        "https://"
                    )

                )

            ):

                return value


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
        # 1. IDENTIFIER URL
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


            if local_name != "identifier":

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
