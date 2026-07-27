import io
import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAOODSParser:

    def __init__(
        self,
        xml_source
    ):

        self.xml_source = xml_source


    # =========================================================
    # PARSER LE CATALOGUE AGRIS
    # =========================================================

    def parse(self):

        print(
            "[FAO ODS PARSER] "
            "Lecture du catalogue AGRIS..."
        )

        try:

            # =================================================
            # 1. EXTRAIRE LE CONTENU XML
            # =================================================

            xml_content = self._extract_xml_content(
                self.xml_source
            )


            if not xml_content:

                print(
                    "[FAO ODS PARSER] "
                    "Aucun contenu XML disponible."
                )

                return []


            print(
                "[FAO ODS PARSER] "
                f"XML disponible : "
                f"{len(xml_content)} octets."
            )


            # =================================================
            # 2. PARSER LE XML
            # =================================================

            if isinstance(
                xml_content,
                bytes
            ):

                root = ET.fromstring(
                    xml_content
                )

            elif isinstance(
                xml_content,
                str
            ):

                root = ET.fromstring(
                    xml_content.encode(
                        "utf-8"
                    )
                )

            else:

                raise ValueError(
                    "Le contenu XML doit être "
                    "de type bytes ou str."
                )


            print(
                "[FAO ODS PARSER] "
                f"Root XML : {root.tag}"
            )


            # =================================================
            # 3. NAMESPACES
            # =================================================

            namespaces = {

                "dc":
                    "http://purl.org/dc/elements/1.1/",

                "dct":
                    "http://purl.org/dc/terms/",

                "dcat":
                    "http://www.w3.org/ns/dcat#",

                "dctypes":
                    "http://purl.org/dc/dcmitype/",

                "xsi":
                    "http://www.w3.org/2001/XMLSchema-instance",

            }


            # =================================================
            # 4. TROUVER LES DATASETS
            # =================================================

            datasets = root.findall(
                ".//dcat:Dataset",
                namespaces
            )


            print(
                "[FAO ODS PARSER] "
                f"{len(datasets)} "
                "dcat:Dataset trouvé(s)."
            )


            # =================================================
            # 5. DEBUG FALLBACK
            # =================================================

            if not datasets:

                print(
                    "[FAO ODS PARSER] "
                    "Recherche générique des datasets..."
                )

                datasets = []

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


                print(
                    "[FAO ODS PARSER] "
                    f"{len(datasets)} dataset(s) "
                    "trouvé(s) avec le fallback."
                )


            # =================================================
            # 6. CONVERTIR EN DOCUMENTS
            # =================================================

            documents = []


            for index, dataset in enumerate(
                datasets,
                start=1
            ):

                try:

                    # -----------------------------------------
                    # TITRE
                    # -----------------------------------------

                    title = self._get_text(
                        dataset,
                        [
                            "dc:title",
                            "dct:title",
                        ],
                        namespaces
                    )


                    if not title:

                        title = (
                            f"Dataset AGRIS {index}"
                        )


                    # -----------------------------------------
                    # DESCRIPTION
                    # -----------------------------------------

                    description = self._get_text(
                        dataset,
                        [
                            "dc:description",
                            "dct:description",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # IDENTIFIANT
                    # -----------------------------------------

                    identifier = self._get_text(
                        dataset,
                        [
                            "dc:identifier",
                            "dct:identifier",
                        ],
                        namespaces
                    )


                    # -----------------------------------------
                    # DATE
                    # -----------------------------------------

                    date_value = self._get_text(
                        dataset,
                        [
                            "dct:modified",
                            "dct:issued",
                            "dc:date",
                        ],
                        namespaces
                    )


                    published_at = (
                        self._parse_date(
                            date_value
                        )
                    )


                    # -----------------------------------------
                    # URL DATASET
                    # -----------------------------------------

                    url = self._get_dataset_url(
                        dataset,
                        namespaces
                    )


                    # -----------------------------------------
                    # IMPORTANT
                    #
                    # Nous ne gardons ici que les datasets
                    # qui possèdent une vraie URL HTTP.
                    # -----------------------------------------

                    if not url:

                        print(
                            "[FAO ODS PARSER] "
                            f"Dataset {index} ignoré : "
                            "aucune URL."
                        )

                        continue


                    # -----------------------------------------
                    # CONTENU
                    # -----------------------------------------

                    content_parts = [
                        f"Titre : {title}"
                    ]


                    if description:

                        content_parts.append(
                            "Description : "
                            f"{description}"
                        )


                    if identifier:

                        content_parts.append(
                            "Identifiant : "
                            f"{identifier}"
                        )


                    content_parts.append(
                        f"URL : {url}"
                    )


                    content = "\n\n".join(
                        content_parts
                    )


                    # -----------------------------------------
                    # DONNÉES DU DOCUMENT
                    # -----------------------------------------

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

                        "document_type":
                            "agricultural_dataset",

                        "description":
                            description,

                        "content":
                            content,

                    }


                    # -----------------------------------------
                    # NE FOURNIR QUE LES CHAMPS ACCEPTÉS
                    # PAR DOCUMENTMETADATA
                    # -----------------------------------------

                    allowed_fields = (
                        DocumentMetadata
                        .model_fields
                    )


                    filtered_data = {

                        key: value

                        for key, value
                        in document_data.items()

                        if key in allowed_fields

                    }


                    document = DocumentMetadata(
                        **filtered_data
                    )


                    documents.append(
                        document
                    )


                except Exception as e:

                    print(
                        "[FAO ODS PARSER] "
                        f"Dataset {index} ignoré : "
                        f"{e}"
                    )


            print(
                "[FAO ODS PARSER] "
                f"{len(documents)} "
                "dataset(s) analysé(s)."
            )


            return documents


        except ET.ParseError as e:

            print(
                "[FAO ODS PARSER] "
                f"Erreur XML : {e}"
            )

            return []


        except Exception as e:

            print(
                "[FAO ODS PARSER] "
                f"Erreur parsing : {e}"
            )

            return []


    # =========================================================
    # EXTRAIRE LE XML DE LA SOURCE
    # =========================================================

    def _extract_xml_content(
        self,
        source
    ):

        # -----------------------------------------------------
        # NOUVELLE ARCHITECTURE :
        # DICTIONNAIRE EN MÉMOIRE
        # -----------------------------------------------------

        if isinstance(
            source,
            dict
        ):

            return source.get(
                "content"
            )


        # -----------------------------------------------------
        # BYTES DIRECTEMENT
        # -----------------------------------------------------

        if isinstance(
            source,
            bytes
        ):

            return source


        # -----------------------------------------------------
        # STRING
        #
        # Peut être du XML directement.
        # -----------------------------------------------------

        if isinstance(
            source,
            str
        ):

            if source.lstrip().startswith(
                "<"
            ):

                return source


        # -----------------------------------------------------
        # ANCIENNE ARCHITECTURE :
        # PATH / CHEMIN
        #
        # Conservée temporairement pour compatibilité.
        # -----------------------------------------------------

        try:

            from pathlib import Path

            path = Path(
                source
            )

            if path.exists():

                return path.read_bytes()

        except Exception:

            pass


        return None


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

                    return (
                        child.text.strip()
                    )


            except Exception:

                pass


        return None


    # =========================================================
    # EXTRAIRE URL DATASET
    # =========================================================

    def _get_dataset_url(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # 1. DOWNLOAD URL
        # -----------------------------------------------------

        candidates = [

            ".//dcat:downloadURL",

            ".//dcat:accessURL",

            ".//dcat:landingPage",

            "dct:identifier",

            "dc:identifier",

        ]


        for path in candidates:

            try:

                nodes = element.findall(
                    path,
                    namespaces
                )


                for node in nodes:

                    # -----------------------------------------
                    # URL DANS LE TEXTE
                    # -----------------------------------------

                    if (
                        node.text
                        and node.text.strip()
                    ):

                        value = (
                            node.text.strip()
                        )


                        if value.startswith(
                            (
                                "http://",
                                "https://"
                            )
                        ):

                            return value


                    # -----------------------------------------
                    # URL DANS UN ATTRIBUT
                    # -----------------------------------------

                    for attribute_value in (
                        node.attrib.values()
                    ):

                        if not attribute_value:

                            continue


                        value = str(
                            attribute_value
                        ).strip()


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
        # 2. FALLBACK GÉNÉRIQUE
        # -----------------------------------------------------

        for child in element.iter():

            if (
                child.text
                and child.text.strip()
            ):

                value = (
                    child.text.strip()
                )


                if (
                    value.startswith(
                        (
                            "http://",
                            "https://"
                        )
                    )
                    and
                    ".xml" in value.lower()
                ):

                    return value


        return None


    # =========================================================
    # CONVERTIR DATE
    # =========================================================

    def _parse_date(
        self,
        value
    ):

        if not value:

            return None


        try:

            return date.fromisoformat(
                value[:10]
            )


        except Exception:

            return None
