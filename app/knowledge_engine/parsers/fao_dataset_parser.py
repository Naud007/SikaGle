import xml.etree.ElementTree as ET

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des fichiers XML individuels
        provenant des datasets AGRIS de la FAO.
        """
        pass

    def parse(self, xml_path):
        """
        Parse un fichier XML AGRIS et retourne
        une liste de DocumentMetadata.
        """

        print(
            f"[FAO DATASET PARSER] "
            f"Lecture : {xml_path}"
        )

        documents = []

        try:

            # -------------------------------------------------
            # 1. Charger le XML
            # -------------------------------------------------

            tree = ET.parse(
                xml_path
            )

            root = tree.getroot()

            # -------------------------------------------------
            # 2. Namespaces possibles AGRIS
            # -------------------------------------------------

            namespaces = {
                "dc": "http://purl.org/dc/elements/1.1/",
                "dct": "http://purl.org/dc/terms/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "agr": "http://purl.org/agris/",
            }

            # -------------------------------------------------
            # 3. Rechercher les ressources
            # -------------------------------------------------

            records = []

            # Cas 1 : RDF Description
            records.extend(
                root.findall(
                    ".//rdf:Description",
                    {
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                    }
                )
            )

            # Cas 2 : Dataset
            records.extend(
                root.findall(
                    ".//dcat:Dataset",
                    namespaces
                )
            )

            # Cas 3 : Tout élément contenant un titre
            if not records:

                for element in root.iter():

                    title = (
                        element.find(
                            "dc:title",
                            namespaces
                        )
                    )

                    if (
                        title is not None
                        and title.text
                    ):

                        records.append(
                            element
                        )

            print(
                f"[FAO DATASET PARSER] "
                f"{len(records)} notice(s) potentielle(s) trouvée(s)."
            )

            # -------------------------------------------------
            # 4. Parcourir les notices
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
                    # DESCRIPTION / ABSTRACT
                    # -----------------------------------------

                    description = self._get_text(
                        record,
                        [
                            "dc:description",
                            "dct:description",
                            "description",
                            "agr:abstract",
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
                    # IDENTIFIANT
                    # -----------------------------------------

                    identifier = self._get_text(
                        record,
                        [
                            "dc:identifier",
                            "dct:identifier",
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
                        ],
                        namespaces
                    )

                    if not source:

                        source = (
                            "FAO AGRIS"
                        )

                    # -----------------------------------------
                    # SI PAS D'URL
                    # -----------------------------------------

                    if not url:

                        if identifier:

                            url = (
                                f"https://agris.fao.org/"
                                f"search/en/providers/"
                                f"122436/records/"
                                f"{identifier}"
                            )

                        else:

                            url = (
                                "https://agris.fao.org/"
                            )

                    # -----------------------------------------
                    # CRÉATION DOCUMENT
                    # -----------------------------------------

                    document_data = {
                        "title": title,
                        "url": url,
                        "description": description,
                        "source": source,
                    }

                    document = (
                        DocumentMetadata(
                            **document_data
                        )
                    )

                    documents.append(
                        document
                    )

                except Exception as e:

                    print(
                        f"[FAO DATASET PARSER] "
                        f"Notice ignorée : {e}"
                    )

            print(
                f"[FAO DATASET PARSER] "
                f"{len(documents)} document(s) analysé(s)."
            )

            return documents

        except ET.ParseError as e:

            print(
                f"[FAO DATASET PARSER] "
                f"Erreur XML : {e}"
            )

            return []

        except Exception as e:

            print(
                f"[FAO DATASET PARSER] "
                f"Erreur lecture : {e}"
            )

            return []

    # =========================================================
    # OUTILS INTERNES
    # =========================================================

    def _get_text(
        self,
        element,
        paths,
        namespaces
    ):
        """
        Recherche le premier texte disponible
        parmi plusieurs chemins XML.
        """

        for path in paths:

            # Recherche avec namespace
            try:

                child = element.find(
                    path,
                    namespaces
                )

                if (
                    child is not None
                    and child.text
                ):

                    return child.text.strip()

            except Exception:

                pass

            # Recherche directe dans les enfants
            for child in element:

                tag = child.tag

                if not isinstance(
                    tag,
                    str
                ):
                    continue

                local_name = (
                    tag.split("}")[-1]
                )

                expected_name = (
                    path.split(":")[-1]
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

    def _get_url(
        self,
        element,
        namespaces
    ):
        """
        Recherche une URL dans une notice AGRIS.
        """

        # -----------------------------------------
        # 1. dc:identifier
        # -----------------------------------------

        identifier = self._get_text(
            element,
            [
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

        # -----------------------------------------
        # 2. dcat:landingPage
        # -----------------------------------------

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

        # -----------------------------------------
        # 3. dcat:accessURL
        # -----------------------------------------

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

        # -----------------------------------------
        # 4. Recherche générique
        # -----------------------------------------

        for child in element.iter():

            if not isinstance(
                child.tag,
                str
            ):

                continue

            local_name = (
                child.tag.split("}")[-1]
            )

            if local_name.lower() in [
                "identifier",
                "url",
                "landingPage",
                "accessURL",
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
