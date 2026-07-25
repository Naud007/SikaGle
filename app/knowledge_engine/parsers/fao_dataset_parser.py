```python
import re
import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):

        """
        Parser robuste des fichiers XML provenant
        des datasets AGRIS / FAO.

        Objectifs :

        - récupérer les métadonnées AGRIS ;
        - gérer plusieurs namespaces XML ;
        - récupérer les titres ;
        - récupérer les résumés ;
        - récupérer les auteurs ;
        - récupérer les organismes ;
        - récupérer les langues ;
        - récupérer les années ;
        - récupérer les mots-clés ;
        - récupérer les pays ;
        - récupérer les cultures ;
        - récupérer les identifiants ;
        - récupérer les URL ;
        - construire un contenu riche pour le RAG.
        """

        pass


    # =========================================================
    # PARSER PRINCIPAL
    # =========================================================

    def parse(
        self,
        xml_path
    ):

        print(
            f"[FAO DATASET PARSER] "
            f"Lecture : {xml_path}"
        )

        documents = []

        try:

            # =================================================
            # 1. CHARGER LE XML
            # =================================================

            tree = ET.parse(
                xml_path
            )

            root = tree.getroot()

            print(
                f"[FAO DATASET PARSER] "
                f"Racine XML : "
                f"{self._local_name(root.tag)}"
            )


            # =================================================
            # 2. ANALYSER LES NAMESPACES
            # =================================================

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

                "agrovoc":
                    "http://aims.fao.org/aos/agrovoc/",

            }


            # =================================================
            # 3. RECHERCHER LES NOTICES
            # =================================================

            records = []


            # -------------------------------------------------
            # RDF DESCRIPTION
            # -------------------------------------------------

            for element in root.iter():

                local_name = (
                    self._local_name(
                        element.tag
                    )
                )

                if local_name.lower() in [

                    "description",

                    "record",

                    "dataset",

                    "item",

                    "entry",

                ]:

                    records.append(
                        element
                    )


            # -------------------------------------------------
            # SUPPRESSION DES DOUBLONS
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


            # =================================================
            # 4. FALLBACK : RACINE COMME NOTICE
            # =================================================

            if not records:

                records = [
                    root
                ]


            print(

                f"[FAO DATASET PARSER] "

                f"{len(records)} "
                f"élément(s) candidat(s) trouvé(s)."

            )


            # =================================================
            # 5. PARCOURIR LES NOTICES
            # =================================================

            for index, record in enumerate(

                records,

                start=1

            ):

                try:

                    document = (
                        self._parse_record(
                            record,
                            namespaces
                        )
                    )


                    if document:

                        documents.append(
                            document
                        )


                        if index <= 5:

                            print(

                                f"[FAO DATASET PARSER] "

                                f"Exemple {index} : "

                                f"{document.model_dump()}"

                            )


                except Exception as e:

                    print(

                        f"[FAO DATASET PARSER] "

                        f"Notice {index} ignorée : "

                        f"{e}"

                    )


            # =================================================
            # 6. DÉDUPLICATION
            # =================================================

            documents = (
                self._deduplicate_documents(
                    documents
                )
            )


            print(

                f"[FAO DATASET PARSER] "

                f"{len(documents)} "
                f"document(s) analysé(s) "
                f"après déduplication."

            )


            return documents


        except ET.ParseError as e:

            print(

                f"[FAO DATASET PARSER] "

                f"Erreur XML : "

                f"{e}"

            )

            return []


        except FileNotFoundError as e:

            print(

                f"[FAO DATASET PARSER] "

                f"Fichier introuvable : "

                f"{e}"

            )

            return []


        except Exception as e:

            print(

                f"[FAO DATASET PARSER] "

                f"Erreur lecture : "

                f"{e}"

            )

            return []


    # =========================================================
    # PARSER D'UNE NOTICE
    # =========================================================

    def _parse_record(
        self,
        record,
        namespaces
    ):

        # =====================================================
        # TITRE
        # =====================================================

        title = self._get_text(

            record,

            [

                "title",

                "dc:title",

                "dct:title",

                "agr:title",

                "name",

            ],

            namespaces

        )


        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = self._get_text(

            record,

            [

                "description",

                "dc:description",

                "dct:description",

                "agr:description",

                "abstract",

                "dc:abstract",

                "dct:abstract",

                "agr:abstract",

                "summary",

            ],

            namespaces

        )


        # =====================================================
        # RÉSUMÉ
        # =====================================================

        abstract = self._get_text(

            record,

            [

                "abstract",

                "dc:abstract",

                "dct:abstract",

                "agr:abstract",

                "summary",

                "description",

            ],

            namespaces

        )


        # =====================================================
        # AUTEURS
        # =====================================================

        authors = self._get_all_text(

            record,

            [

                "creator",

                "dc:creator",

                "dct:creator",

                "author",

                "contributor",

                "dc:contributor",

                "dct:contributor",

            ],

            namespaces

        )


        # =====================================================
        # ORGANISME / ÉDITEUR
        # =====================================================

        publisher = self._get_text(

            record,

            [

                "publisher",

                "dc:publisher",

                "dct:publisher",

                "organization",

                "organisation",

                "institution",

                "agency",

            ],

            namespaces

        )


        # =====================================================
        # LANGUE
        # =====================================================

        language = self._get_text(

            record,

            [

                "language",

                "dc:language",

                "dct:language",

            ],

            namespaces

        )


        # =====================================================
        # DATE / ANNÉE
        # =====================================================

        year = self._get_text(

            record,

            [

                "date",

                "dc:date",

                "dct:date",

                "issued",

                "dct:issued",

                "year",

            ],

            namespaces

        )


        # =====================================================
        # MOTS-CLÉS
        # =====================================================

        keywords = self._get_all_text(

            record,

            [

                "subject",

                "dc:subject",

                "dct:subject",

                "keyword",

                "keywords",

                "descriptor",

                "theme",

            ],

            namespaces

        )


        # =====================================================
        # CULTURES
        # =====================================================

        crops = self._get_all_text(

            record,

            [

                "crop",

                "crops",

                "culture",

                "cultures",

                "commodity",

                "plant",

                "species",

            ],

            namespaces

        )


        # =====================================================
        # PAYS / ZONE GÉOGRAPHIQUE
        # =====================================================

        countries = self._get_all_text(

            record,

            [

                "country",

                "countries",

                "place",

                "coverage",

                "dc:coverage",

                "dct:spatial",

                "spatial",

                "location",

                "geographic",

            ],

            namespaces

        )


        # =====================================================
        # SOURCE
        # =====================================================

        source = self._get_text(

            record,

            [

                "source",

                "dc:source",

                "dct:source",

            ],

            namespaces

        )


        if not source:

            source = (
                "FAO AGRIS"
            )


        # =====================================================
        # IDENTIFIANT
        # =====================================================

        identifier = self._get_text(

            record,

            [

                "identifier",

                "dc:identifier",

                "dct:identifier",

                "id",

                "recordId",

                "recordID",

            ],

            namespaces

        )


        # =====================================================
        # URL
        # =====================================================

        url = self._get_url(

            record,

            namespaces

        )


        # =====================================================
        # FALLBACK URL AGRIS
        # =====================================================

        if not url and identifier:

            clean_identifier = (
                identifier.strip()
            )

            url = (

                "https://agris.fao.org/"

                "search/en/providers/"

                "122436/records/"

                f"{clean_identifier}"

            )


        # =====================================================
        # TITRE PAR DÉFAUT
        # =====================================================

        if not title:

            # Essayer de trouver un texte
            # significatif dans la notice.

            title = self._find_best_text(
                record
            )


        if not title:

            title = (
                "Document AGRIS"
            )


        # =====================================================
        # LANGUE PAR DÉFAUT
        # =====================================================

        if not language:

            language = (
                "fr"
            )


        # =====================================================
        # ANNÉE
        # =====================================================

        if year:

            year = self._extract_year(
                year
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

                f"Description : "
                f"{description}"

            )


        if abstract:

            if (
                abstract
                != description
            ):

                content_parts.append(

                    f"Résumé : "
                    f"{abstract}"

                )


        if authors:

            content_parts.append(

                "Auteur(s) : "
                + ", ".join(
                    authors
                )

            )


        if publisher:

            content_parts.append(

                f"Organisme : "
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


        if crops:

            content_parts.append(

                "Culture(s) : "
                + ", ".join(
                    crops
                )

            )


        if countries:

            content_parts.append(

                "Zone géographique : "
                + ", ".join(
                    countries
                )

            )


        if source:

            content_parts.append(

                f"Source : "
                f"{source}"

            )


        if identifier:

            content_parts.append(

                f"Identifiant : "
                f"{identifier}"

            )


        if url:

            content_parts.append(

                f"URL : "
                f"{url}"

            )


        content = (

            "\n\n"

            .join(
                content_parts
            )

        )


        # =====================================================
        # CONSTRUIRE LE DOCUMENT
        # =====================================================

        document_data = {

            "title":
                title,

            "url":
                url,

            "description":
                description
                or abstract,

            "source":
                source,

            "content":
                content,

        }


        # =====================================================
        # AJOUTER LES CHAMPS OPTIONNELS
        # SI LE SCHÉMA LES ACCEPTE
        # =====================================================

        optional_fields = {

            "author":
                authors,

            "authors":
                authors,

            "publisher":
                publisher,

            "language":
                language,

            "year":
                year,

            "keywords":
                keywords,

            "crop":
                crops[0]
                if crops
                else None,

            "crops":
                crops,

            "country":
                countries[0]
                if countries
                else None,

            "countries":
                countries,

            "identifier":
                identifier,

        }


        document_fields = (

            DocumentMetadata

            .model_fields

        )


        for key, value in (

            optional_fields.items()

        ):

            if (

                key
                in document_fields

                and value

            ):

                document_data[
                    key
                ] = value


        # =====================================================
        # FILTRER LES CHAMPS
        # =====================================================

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
            # RECHERCHE PAR NAMESPACE
            # -------------------------------------------------

            try:

                child = (

                    element.find(

                        path,

                        namespaces

                    )

                )


                if (

                    child is not None

                    and child.text

                    and child.text.strip()

                ):

                    return (

                        self._clean_text(

                            child.text

                        )

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

                    self._local_name(

                        child.tag

                    )

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

                            self._clean_text(

                                child.text

                            )

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

                self._local_name(

                    child.tag

                )

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

                        self._clean_text(

                            child.text

                        )

                    )


                    if (

                        value

                        and

                        value not in values

                    ):

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

        # =====================================================
        # 1. IDENTIFIER
        # =====================================================

        identifier = self._get_text(

            element,

            [

                "identifier",

                "dc:identifier",

                "dct:identifier",

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


        # =====================================================
        # 2. LANDING PAGE
        # =====================================================

        for name in [

            "landingPage",

            "landingpage",

            "url",

            "URI",

            "uri",

            "accessURL",

            "accessUrl",

            "accessurl",

        ]:

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

                    local_name.lower()

                    == name.lower()

                ):

                    # -----------------------------------------
                    # TEXTE
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # ATTRIBUT RDF RESOURCE
                    # -----------------------------------------

                    for attribute_name in [

                        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource",

                        "resource",

                        "href",

                        "url",

                    ]:

                        value = (

                            child.attrib.get(

                                attribute_name

                            )

                        )


                        if value:

                            if value.startswith(

                                (

                                    "http://",

                                    "https://"

                                )

                            ):

                                return value


        # =====================================================
        # 3. RECHERCHE DANS LES ATTRIBUTS
        # =====================================================

        for child in element.iter():

            if not isinstance(

                child.tag,

                str

            ):

                continue


            for value in child.attrib.values():

                if not isinstance(

                    value,

                    str

                ):

                    continue


                value = value.strip()


                if value.startswith(

                    (

                        "http://",

                        "https://"

                    )

                ):

                    return value


        # =====================================================
        # 4. RECHERCHE DE TEXTE CONTENANT UNE URL
        # =====================================================

        for child in element.iter():

            if not isinstance(

                child.tag,

                str

            ):

                continue


            if not child.text:

                continue


            text = child.text.strip()


            match = re.search(

                r"https?://[^\s<>\"']+",

                text

            )


            if match:

                return (

                    match.group(
                        0
                    )

                )


        return None


    # =========================================================
    # TROUVER LE MEILLEUR TEXTE
    # =========================================================

    def _find_best_text(
        self,
        element
    ):

        candidates = []


        for child in element.iter():

            if not isinstance(

                child.tag,

                str

            ):

                continue


            if not child.text:

                continue


            text = (

                self._clean_text(

                    child.text

                )

            )


            if not text:

                continue


            if len(text) < 10:

                continue


            local_name = (

                self._local_name(

                    child.tag

                )

                .lower()

            )


            # Donner la priorité
            # aux champs susceptibles
            # d'être des titres.

            priority = 0


            if local_name in [

                "title",

                "name",

            ]:

                priority = 100


            elif local_name in [

                "subject",

                "identifier",

            ]:

                priority = 50


            candidates.append(

                (

                    priority,

                    len(text),

                    text

                )

            )


        if not candidates:

            return None


        candidates.sort(

            key=lambda item: (

                item[0],

                -item[1]

            ),

            reverse=True

        )


        return candidates[0][2]


    # =========================================================
    # EXTRAIRE ANNÉE
    # =========================================================

    def _extract_year(
        self,
        value
    ):

        if not value:

            return None


        match = re.search(

            r"\b(19|20)\d{2}\b",

            str(value)

        )


        if match:

            return match.group(
                0
            )


        return str(
            value
        ).strip()


    # =========================================================
    # NETTOYER UN TEXTE
    # =========================================================

    def _clean_text(
        self,
        text
    ):

        if not text:

            return None


        text = str(
            text
        )


        text = (

            text

            .replace(
                "\n",
                " "
            )

            .replace(
                "\r",
                " "
            )

            .replace(
                "\t",
                " "
            )

        )


        text = re.sub(

            r"\s+",

            " ",

            text

        )


        text = text.strip()


        return text or None


    # =========================================================
    # NOM LOCAL XML
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

            return (

                tag

                .split(

                    "}",

                    1

                )[1]

            )


        return tag


    # =========================================================
    # DÉDUPLICATION
    # =========================================================

    def _deduplicate_documents(
        self,
        documents
    ):

        unique_documents = []

        seen = set()


        for document in documents:

            data = (

                document.model_dump(

                    mode="json"

                )

            )


            url = (

                data.get(
                    "url"
                )

            )


            title = (

                data.get(
                    "title"
                )

            )


            content = (

                data.get(
                    "content"
                )

            )


            # Priorité URL

            if url:

                key = (

                    "url",

                    str(url).strip().lower()

                )


            # Sinon titre

            elif title:

                key = (

                    "title",

                    str(title).strip().lower()

                )


            # Sinon contenu

            else:

                key = (

                    "content",

                    str(content).strip().lower()

                )


            if key in seen:

                continue


            seen.add(
                key
            )


            unique_documents.append(

                document

            )


        return unique_documents
```
