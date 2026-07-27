import re
import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAODatasetParser:

    def __init__(self):
        """
        Parser des datasets XML AGRIS.

        Le parser reçoit directement le contenu XML
        téléchargé en mémoire.

        Objectifs :
        - extraire les publications AGRIS ;
        - conserver les métadonnées réelles ;
        - ne jamais inventer un pays ou une culture ;
        - préparer des documents propres pour le RAG.
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


            # Le root peut lui-même être une notice.

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
                f"{len(records)} "
                "notice(s) trouvée(s)."
            )


            if not records:

                return []


            # =================================================
            # 6. PARSER LES NOTICES
            # =================================================

            for index, record in enumerate(
                records,
                start=1
            ):

                try:

                    document = (
                        self._parse_record(
                            record=record,
                            namespaces=namespaces,
                            filename=filename,
                            source_url=source_url,
                            index=index
                        )
                    )


                    if document:

                        documents.append(
                            document
                        )


                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {index} ignorée : "
                        f"{e}"
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
    # PARSER UNE NOTICE
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


        title = self._clean_text(
            title
        )


        # =====================================================
        # DESCRIPTION
        # =====================================================

        description = self._get_text(
            record,
            [
                "dc:description",
                "dct:description",
                "dc:abstract",
                "dct:abstract",
            ],
            namespaces
        )


        description = self._clean_text(
            description
        )


        # =====================================================
        # AUTEURS
        # =====================================================

        authors = self._get_all_text(
            record,
            [
                "dc:creator",
                "dct:creator",
                "dc:contributor",
                "dct:contributor",
            ],
            namespaces
        )


        # =====================================================
        # DATE
        # =====================================================

        date_value = self._get_text(
            record,
            [
                "dc:date",
                "dct:date",
                "dct:issued",
                "dct:created",
                "dct:modified",
            ],
            namespaces
        )


        published_at = (
            self._parse_date(
                date_value
            )
        )


        year = (
            self._extract_year(
                date_value
            )
        )


        # =====================================================
        # TYPE DU DOCUMENT
        # =====================================================

        publication_type = self._get_text(
            record,
            [
                "dc:type",
                "dct:type",
            ],
            namespaces
        )


        publication_type = (
            self._clean_text(
                publication_type
            )
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


        keywords = (
            self._clean_list(
                keywords
            )
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


        publication_source = (
            self._clean_text(
                publication_source
            )
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


        publisher = self._clean_text(
            publisher
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


        language = (
            self._normalize_language(
                language
            )
        )


        # =====================================================
        # IDENTIFIANT AGRIS
        # =====================================================

        agris_id = self._get_agris_id(
            record,
            namespaces
        )


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

                url = str(
                    source_url
                ).strip()

            else:

                url = (
                    "https://agris.fao.org/"
                )


        # =====================================================
        # ZONE GÉOGRAPHIQUE
        # =====================================================

        geographic_values = (
            self._get_geographic_values(
                record
            )
        )


        country = (
            self._detect_country(
                geographic_values,
                title,
                description
            )
        )


        zone_geographique = (
            self._build_geographic_zone(
                geographic_values,
                country
            )
        )


        # =====================================================
        # CULTURE
        # =====================================================

        culture = (
            self._detect_crop(
                title=title,
                description=description,
                keywords=keywords
            )
        )


        # =====================================================
        # CONTENU POUR LE RAG
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


        if year:

            content_parts.append(
                f"Année : {year}"
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


        if culture:

            content_parts.append(
                f"Culture : {culture}"
            )


        if country:

            content_parts.append(
                f"Pays / contexte géographique : {country}"
            )


        elif zone_geographique:

            content_parts.append(
                "Zone géographique : "
                f"{zone_geographique}"
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
        # DOCUMENT STANDARDISÉ
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

            "country":
                country,

            "crop":
                culture,

            "culture":
                culture,

            "document_type":
                (
                    publication_type
                    or
                    "agricultural_publication"
                ),

            "content":
                content,

            "description":
                description,

            "zone_geographique":
                zone_geographique,

            "mots_cles":
                keywords,

        }


        # =====================================================
        # NE PAS FORCER DE FAUSSES VALEURS
        # =====================================================

        document_data = {

            key: value

            for key, value
            in document_data.items()

            if value is not None

        }


        # =====================================================
        # NE GARDER QUE LES CHAMPS DU SCHÉMA
        # =====================================================

        document_fields = (
            DocumentMetadata.model_fields
        )


        filtered_data = {

            key: value

            for key, value
            in document_data.items()

            if key in document_fields

        }


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

                    return (
                        child.text.strip()
                    )


            except Exception:

                pass


        expected_names = {

            path
            .split(":")[-1]
            .lower()

            for path in paths

        }


        for child in element.iter():

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

            local_name = (
                self._local_name(
                    child.tag
                )
                .lower()
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

                value = (
                    self._clean_text(
                        child.text
                    )
                )


                if (
                    value
                    and value not in values
                ):

                    values.append(
                        value
                    )


        return values


    # =========================================================
    # EXTRAIRE INFORMATIONS GÉOGRAPHIQUES
    # =========================================================

    def _get_geographic_values(
        self,
        element
    ):

        geographic_names = {

            "coverage",
            "spatial",
            "location",
            "geographiccoverage",
            "geographic",
            "country",

        }


        values = []


        for child in element.iter():

            local_name = (
                self._local_name(
                    child.tag
                )
                .lower()
            )


            if (
                local_name
                not in geographic_names
            ):

                continue


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
                    and value not in values
                ):

                    values.append(
                        value
                    )


        return values


    # =========================================================
    # CONSTRUIRE ZONE GÉOGRAPHIQUE
    # =========================================================

    def _build_geographic_zone(
        self,
        geographic_values,
        country
    ):

        if geographic_values:

            return ", ".join(
                geographic_values[:5]
            )


        if country:

            return country


        return None


    # =========================================================
    # DÉTECTER PAYS
    # =========================================================

    def _detect_country(
        self,
        geographic_values,
        title,
        description
    ):

        countries = {

            "benin":
                "Bénin",

            "bénin":
                "Bénin",

            "nigeria":
                "Nigeria",

            "niger":
                "Niger",

            "togo":
                "Togo",

            "ghana":
                "Ghana",

            "burkina faso":
                "Burkina Faso",

            "mali":
                "Mali",

            "senegal":
                "Sénégal",

            "sénégal":
                "Sénégal",

            "cameroon":
                "Cameroun",

            "cameroun":
                "Cameroun",

            "bulgaria":
                "Bulgarie",

            "bulgarie":
                "Bulgarie",

            "nepal":
                "Népal",

            "népal":
                "Népal",

            "kenya":
                "Kenya",

            "uganda":
                "Ouganda",

            "ethiopia":
                "Éthiopie",

            "ethiopie":
                "Éthiopie",

            "éthiopie":
                "Éthiopie",

            "ivory coast":
                "Côte d'Ivoire",

            "côte d'ivoire":
                "Côte d'Ivoire",

            "cote d'ivoire":
                "Côte d'Ivoire",

        }


        # -----------------------------------------------------
        # PRIORITÉ AUX MÉTADONNÉES GÉOGRAPHIQUES
        # -----------------------------------------------------

        geographic_text = " ".join(
            geographic_values
        ).lower()


        for name, normalized in countries.items():

            if self._contains_word(
                geographic_text,
                name
            ):

                return normalized


        # -----------------------------------------------------
        # FALLBACK TITRE + DESCRIPTION
        # -----------------------------------------------------

        combined_text = (
            f"{title or ''} "
            f"{description or ''}"
        ).lower()


        for name, normalized in countries.items():

            if self._contains_word(
                combined_text,
                name
            ):

                return normalized


        # IMPORTANT :
        # aucun pays n'est inventé.

        return None


    # =========================================================
    # DÉTECTER CULTURE
    # =========================================================

    def _detect_crop(
        self,
        title,
        description,
        keywords
    ):

        crop_names = {

            "maize":
                "maïs",

            "corn":
                "maïs",

            "maïs":
                "maïs",

            "maize crop":
                "maïs",

            "rice":
                "riz",

            "riz":
                "riz",

            "cassava":
                "manioc",

            "manioc":
                "manioc",

            "yam":
                "igname",

            "igname":
                "igname",

            "soybean":
                "soja",

            "soybeans":
                "soja",

            "soya":
                "soja",

            "soja":
                "soja",

            "cotton":
                "coton",

            "coton":
                "coton",

            "tomato":
                "tomate",

            "tomatoes":
                "tomate",

            "tomate":
                "tomate",

            "carrot":
                "carotte",

            "carrots":
                "carotte",

            "carotte":
                "carotte",

            "millet":
                "mil",

            "finger millet":
                "mil",

            "sorghum":
                "sorgho",

            "sorgho":
                "sorgho",

            "wheat":
                "blé",

            "einkorn":
                "blé",

            "emmer":
                "blé",

            "blé":
                "blé",

            "groundnut":
                "arachide",

            "peanut":
                "arachide",

            "arachide":
                "arachide",

            "cowpea":
                "niébé",

            "niébé":
                "niébé",

            "niebe":
                "niébé",

            "cashew":
                "anacarde",

            "cashew nut":
                "anacarde",

            "anacardier":
                "anacarde",

            "anacarde":
                "anacarde",

            "pineapple":
                "ananas",

            "ananas":
                "ananas",

            "banana":
                "banane",

            "plantain":
                "banane plantain",

            "potato":
                "pomme de terre",

            "sweet potato":
                "patate douce",

            "cocoa":
                "cacao",

            "cacao":
                "cacao",

            "coffee":
                "café",

            "café":
                "café",

        }


        # -----------------------------------------------------
        # LES MOTS-CLÉS SONT PRIORITAIRES
        # -----------------------------------------------------

        keyword_text = " ".join(
            keywords or []
        ).lower()


        # -----------------------------------------------------
        # TITRE ENSUITE
        # -----------------------------------------------------

        title_text = (
            title or ""
        ).lower()


        # -----------------------------------------------------
        # DESCRIPTION EN DERNIER
        # -----------------------------------------------------

        description_text = (
            description or ""
        ).lower()


        search_areas = [

            keyword_text,
            title_text,
            description_text,

        ]


        # Les expressions longues doivent passer
        # avant les expressions courtes.

        ordered_crops = sorted(

            crop_names.items(),

            key=lambda item: len(
                item[0]
            ),

            reverse=True

        )


        for text in search_areas:

            for name, normalized in ordered_crops:

                if self._contains_word(
                    text,
                    name
                ):

                    return normalized


        return None


    # =========================================================
    # NORMALISER LANGUE
    # =========================================================

    def _normalize_language(
        self,
        language
    ):

        if not language:

            return None


        value = (
            str(language)
            .strip()
            .lower()
        )


        mapping = {

            "en":
                "en",

            "eng":
                "en",

            "english":
                "en",

            "fr":
                "fr",

            "fra":
                "fr",

            "fre":
                "fr",

            "french":
                "fr",

            "français":
                "fr",

            "pt":
                "pt",

            "por":
                "pt",

            "portuguese":
                "pt",

            "es":
                "es",

            "spa":
                "es",

            "spanish":
                "es",

            "de":
                "de",

            "deu":
                "de",

            "ger":
                "de",

        }


        return mapping.get(
            value,
            value[:10]
        )


    # =========================================================
    # EXTRAIRE IDENTIFIANT AGRIS
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

            return (
                xml_id.strip()
            )


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

                    return (
                        identifier.text.strip()
                    )


        except Exception:

            pass


        return None


    # =========================================================
    # EXTRAIRE URL
    # =========================================================

    def _get_document_url(
        self,
        element,
        namespaces
    ):

        # -----------------------------------------------------
        # DC IDENTIFIER
        # -----------------------------------------------------

        try:

            identifiers = element.findall(
                "dc:identifier",
                namespaces
            )


            # Priorité à type URL

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
                    and self._is_url(
                        value
                    )
                ):

                    return value


            # Ensuite n'importe quelle URL

            for identifier in identifiers:

                if (
                    identifier.text
                    and identifier.text.strip()
                ):

                    value = (
                        identifier.text.strip()
                    )


                    if self._is_url(
                        value
                    ):

                        return value


        except Exception:

            pass


        # -----------------------------------------------------
        # DCT IDENTIFIER
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

                    value = (
                        identifier.text.strip()
                    )


                    if self._is_url(
                        value
                    ):

                        return value


        except Exception:

            pass


        # -----------------------------------------------------
        # FALLBACK
        # -----------------------------------------------------

        allowed_names = {

            "identifier",
            "url",
            "landingpage",
            "accessurl",
            "downloadurl",

        }


        for child in element.iter():

            if (
                not child.text
                or not child.text.strip()
            ):

                continue


            value = (
                child.text.strip()
            )


            if not self._is_url(
                value
            ):

                continue


            local_name = (
                self._local_name(
                    child.tag
                )
                .lower()
            )


            if local_name in allowed_names:

                return value


        return None


    # =========================================================
    # PARSER DATE
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

        match = re.search(
            r"\b(\d{4})-(\d{2})-(\d{2})\b",
            value
        )


        if match:

            try:

                return date(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3))
                )

            except ValueError:

                pass


        # -----------------------------------------------------
        # YYYY
        # -----------------------------------------------------

        year = self._extract_year(
            value
        )


        if year:

            try:

                return date(
                    int(year),
                    1,
                    1
                )

            except ValueError:

                pass


        return None


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


        return None


    # =========================================================
    # NETTOYER TEXTE
    # =========================================================

    def _clean_text(
        self,
        value
    ):

        if not value:

            return None


        value = str(
            value
        )


        # Quelques entités HTML fréquentes.

        replacements = {

            "&nbsp;":
                " ",

            "&#160;":
                " ",

            "\xa0":
                " ",

        }


        for old, new in replacements.items():

            value = value.replace(
                old,
                new
            )


        value = re.sub(
            r"\s+",
            " ",
            value
        )


        value = value.strip()


        return (
            value
            if value
            else None
        )


    # =========================================================
    # NETTOYER LISTE
    # =========================================================

    def _clean_list(
        self,
        values
    ):

        cleaned = []


        for value in (
            values or []
        ):

            value = (
                self._clean_text(
                    value
                )
            )


            if (
                value
                and value not in cleaned
            ):

                cleaned.append(
                    value
                )


        return cleaned


    # =========================================================
    # VÉRIFIER URL
    # =========================================================

    def _is_url(
        self,
        value
    ):

        if not value:

            return False


        return str(
            value
        ).strip().startswith(
            (
                "http://",
                "https://"
            )
        )


    # =========================================================
    # RECHERCHE MOT / EXPRESSION
    # =========================================================

    def _contains_word(
        self,
        text,
        expression
    ):

        if (
            not text
            or not expression
        ):

            return False


        pattern = (

            r"(?<!\w)"
            + re.escape(
                expression.lower()
            )
            + r"(?!\w)"

        )


        return bool(
            re.search(
                pattern,
                text.lower()
            )
        )


    # =========================================================
    # NOM LOCAL TAG XML
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
