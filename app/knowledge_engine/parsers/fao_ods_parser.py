import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    def __init__(self, xml_path):

        self.xml_path = xml_path


    # =========================================================
    # PARSER PRINCIPAL
    # =========================================================

    def parse(self):

        print(
            "[FAO ODS PARSER] "
            "Lecture du catalogue AGRIS..."
        )

        try:

            tree = ET.parse(
                self.xml_path
            )

            root = tree.getroot()

        except Exception as e:

            print(
                "[FAO ODS PARSER] "
                f"Erreur lecture XML : {e}"
            )

            return []


        print(
            "[FAO ODS PARSER] "
            f"Élément racine : {root.tag}"
        )


        # =====================================================
        # NAMESPACES
        # =====================================================

        namespaces = {

            "dc":
                "http://purl.org/dc/elements/1.1/",

            "dct":
                "http://purl.org/dc/terms/",

            "dcat":
                "http://www.w3.org/ns/dcat#",

            "dctypes":
                "http://purl.org/dc/dcmitype/",

            "rdf":
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#",

        }


        # =====================================================
        # RECHERCHER LES DATASETS
        # =====================================================

        datasets = []


        # -----------------------------------------------------
        # 1. dcat:Dataset
        # -----------------------------------------------------

        datasets.extend(
            root.findall(
                ".//dcat:Dataset",
                namespaces
            )
        )


        # -----------------------------------------------------
        # 2. dctypes:Dataset
        # -----------------------------------------------------

        datasets.extend(
            root.findall(
                ".//dctypes:Dataset",
                namespaces
            )
        )


        # -----------------------------------------------------
        # 3. RECHERCHE GÉNÉRIQUE
        # -----------------------------------------------------

        if not datasets:

            print(
                "[FAO ODS PARSER] "
                "Recherche générique des datasets..."
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

                if local_name == "dataset":

                    datasets.append(
                        element
                    )


        # =====================================================
        # SUPPRIMER LES DOUBLONS
        # =====================================================

        unique_datasets = []

        seen = set()


        for dataset in datasets:

            dataset_id = id(
                dataset
            )

            if dataset_id in seen:

                continue

            seen.add(
                dataset_id
            )

            unique_datasets.append(
                dataset
            )


        datasets = unique_datasets


        print(
            "[FAO ODS PARSER] "
            f"{len(datasets)} dataset(s) XML détecté(s)."
        )


        # =====================================================
        # EXTRACTION DES DOCUMENTS
        # =====================================================

        documents = []

        seen_urls = set()


        for dataset in datasets:

            try:

                # =================================================
                # TITRE
                # =================================================

                title = self._get_text(
                    dataset,
                    [
                        "title"
                    ]
                )

                if not title:

                    title = (
                        "Dataset AGRIS"
                    )


                # =================================================
                # DESCRIPTION
                # =================================================

                description = self._get_text(
                    dataset,
                    [
                        "description"
                    ]
                )


                # =================================================
                # DATE
                # =================================================

                date_value = self._get_text(
                    dataset,
                    [
                        "modified",
                        "issued",
                        "date"
                    ]
                )

                published_at = (
                    self._parse_date(
                        date_value
                    )
                )


                # =================================================
                # IDENTIFIANT
                # =================================================

                identifier = self._get_text(
                    dataset,
                    [
                        "identifier"
                    ]
                )


                # =================================================
                # URL
                # =================================================

                url = self._get_dataset_url(
                    dataset
                )


                # =================================================
                # FALLBACK : CHERCHER TOUTE URL XML
                # =================================================

                if not url:

                    url = self._find_xml_url(
                        dataset
                    )


                # =================================================
                # PAS D'URL = PAS DE DATASET TÉLÉCHARGEABLE
                # =================================================

                if not url:

                    print(
                        "[FAO ODS PARSER] "
                        "Dataset ignoré sans URL : "
                        f"{title[:80]}"
                    )

                    continue


                url = str(
                    url
                ).strip()


                # =================================================
                # NOUS VOULONS UN DATASET XML AGRIS
                # =================================================

                if not self._is_agris_dataset_url(
                    url
                ):

                    print(
                        "[FAO ODS PARSER] "
                        "URL ignorée : "
                        f"{url}"
                    )

                    continue


                # =================================================
                # ÉVITER LES DOUBLONS
                # =================================================

                if url in seen_urls:

                    continue


                seen_urls.add(
                    url
                )


                # =================================================
                # CONTENU
                # =================================================

                content_parts = [
                    f"Titre : {title}"
                ]


                if description:

                    content_parts.append(
                        f"Description : {description}"
                    )


                if identifier:

                    content_parts.append(
                        f"Identifiant : {identifier}"
                    )


                content_parts.append(
                    f"URL : {url}"
                )


                content = "\n\n".join(
                    content_parts
                )


                # =================================================
                # DOCUMENT METADATA
                # =================================================

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
                        "en",

                    "country":
                        None,

                    "document_type":
                        "agricultural_dataset",

                    "description":
                        description,

                    "content":
                        content,

                }


                # =================================================
                # NE GARDER QUE LES CHAMPS ACCEPTÉS
                # PAR DocumentMetadata
                # =================================================

                allowed_fields = (
                    DocumentMetadata.model_fields
                )


                filtered_data = {

                    key: value

                    for key, value
                    in document_data.items()

                    if key in allowed_fields

                }


                document = (
                    DocumentMetadata(
                        **filtered_data
                    )
                )


                documents.append(
                    document
                )


                print(
                    "[FAO ODS PARSER] "
                    "Dataset trouvé : "
                    f"{url}"
                )


            except Exception as e:

                print(
                    "[FAO ODS PARSER] "
                    f"Dataset ignoré : {e}"
                )


        # =====================================================
        # FALLBACK GLOBAL
        # =====================================================

        if not documents:

            print(
                "[FAO ODS PARSER] "
                "Aucun dataset structuré exploitable."
            )

            print(
                "[FAO ODS PARSER] "
                "Recherche globale des URLs AGRIS XML..."
            )


            global_urls = (
                self._find_all_agris_xml_urls(
                    root
                )
            )


            for index, url in enumerate(
                global_urls,
                start=1
            ):

                try:

                    filename = (
                        url
                        .rstrip("/")
                        .split("/")[-1]
                    )


                    title = (
                        "AGRIS Open Data Set - "
                        f"{filename}"
                    )


                    document_data = {

                        "title":
                            title,

                        "source":
                            "FAO AGRIS",

                        "url":
                            url,

                        "language":
                            "en",

                        "country":
                            None,

                        "document_type":
                            "agricultural_dataset",

                        "description":
                            (
                                "Dataset XML du catalogue "
                                "FAO AGRIS."
                            ),

                        "content":
                            (
                                f"Titre : {title}\n\n"
                                f"URL : {url}"
                            ),

                    }


                    allowed_fields = (
                        DocumentMetadata.model_fields
                    )


                    filtered_data = {

                        key: value

                        for key, value
                        in document_data.items()

                        if key in allowed_fields

                    }


                    document = (
                        DocumentMetadata(
                            **filtered_data
                        )
                    )


                    documents.append(
                        document
                    )


                    print(
                        "[FAO ODS PARSER] "
                        f"Dataset global {index} : "
                        f"{url}"
                    )


                except Exception as e:

                    print(
                        "[FAO ODS PARSER] "
                        "URL globale ignorée : "
                        f"{e}"
                    )


        print(
            "[FAO ODS PARSER] "
            f"{len(documents)} dataset(s) "
            "finalement disponible(s)."
        )


        return documents


    # =========================================================
    # EXTRAIRE UN TEXTE PAR NOM LOCAL
    # =========================================================

    def _get_text(
        self,
        element,
        names
    ):

        expected_names = {

            name.lower()

            for name in names

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


            if local_name not in expected_names:

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
    # TROUVER URL DATASET
    # =========================================================

    def _get_dataset_url(
        self,
        element
    ):

        preferred_names = [

            "downloadurl",

            "accessurl",

            "landingpage",

            "identifier",

            "source",

        ]


        for expected_name in preferred_names:

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
                    != expected_name
                ):

                    continue


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


                    if self._is_agris_dataset_url(
                        value
                    ):

                        return value


                # -----------------------------------------
                # ATTRIBUTS
                # -----------------------------------------

                for attribute_value in (
                    child.attrib.values()
                ):

                    value = str(
                        attribute_value
                    ).strip()


                    if self._is_agris_dataset_url(
                        value
                    ):

                        return value


        return None


    # =========================================================
    # CHERCHER UNE URL XML DANS UN ÉLÉMENT
    # =========================================================

    def _find_xml_url(
        self,
        element
    ):

        for child in element.iter():

            # -------------------------------------------------
            # TEXTE
            # -------------------------------------------------

            if (
                child.text
                and child.text.strip()
            ):

                value = (
                    child.text.strip()
                )


                if self._is_agris_dataset_url(
                    value
                ):

                    return value


            # -------------------------------------------------
            # ATTRIBUTS
            # -------------------------------------------------

            for attribute_value in (
                child.attrib.values()
            ):

                value = str(
                    attribute_value
                ).strip()


                if self._is_agris_dataset_url(
                    value
                ):

                    return value


        return None


    # =========================================================
    # RECHERCHE GLOBALE DES URLS XML AGRIS
    # =========================================================

    def _find_all_agris_xml_urls(
        self,
        root
    ):

        urls = []

        seen = set()


        for element in root.iter():

            values = []


            if (
                element.text
                and element.text.strip()
            ):

                values.append(
                    element.text.strip()
                )


            for attribute_value in (
                element.attrib.values()
            ):

                values.append(
                    str(
                        attribute_value
                    ).strip()
                )


            for value in values:

                if not self._is_agris_dataset_url(
                    value
                ):

                    continue


                if value in seen:

                    continue


                seen.add(
                    value
                )

                urls.append(
                    value
                )


        return urls


    # =========================================================
    # VÉRIFIER URL AGRIS DATASET
    # =========================================================

    def _is_agris_dataset_url(
        self,
        value
    ):

        if not value:

            return False


        value = str(
            value
        ).strip()


        if not value.startswith(
            (
                "http://",
                "https://"
            )
        ):

            return False


        value_lower = (
            value.lower()
        )


        if (
            "agris.fao.org"
            not in value_lower
        ):

            return False


        if (
            ".xml"
            not in value_lower
        ):

            return False


        # Ne pas considérer le catalogue principal
        # lui-même comme un dataset à télécharger.

        if (
            value_lower.rstrip("/")
            ==
            "https://agris.fao.org/ods/agris.ods.xml"
        ):

            return False


        return True


    # =========================================================
    # PARSER UNE DATE
    # =========================================================

    def _parse_date(
        self,
        value
    ):

        if not value:

            return None


        try:

            return date.fromisoformat(
                str(
                    value
                )[:10]
            )

        except Exception:

            return None
