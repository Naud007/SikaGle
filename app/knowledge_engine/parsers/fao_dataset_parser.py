import re
import io
import xml.etree.ElementTree as ET
from datetime import date

from app.schemas.document import DocumentMetadata


class FAODatasetParser:
    """
    Parser streaming des datasets XML AGRIS de la FAO.

    Le XML est parcouru avec iterparse afin d'éviter de charger
    l'arbre XML complet en mémoire.

    Le parser peut recevoir :
    - bytes
    - str
    - fichier ouvert

    Le parsing accepte un offset et une limite afin de ne produire
    que les documents nécessaires au batch RAG.
    """

    def __init__(self):
        pass

    # =========================================================
    # PARSER PRINCIPAL STREAMING
    # =========================================================

    def parse(
        self,
        xml_content,
        filename=None,
        source_url=None,
        offset=0,
        limit=None,
    ):
        print("=" * 60)
        print(
            "[FAO DATASET PARSER] "
            f"Analyse : {filename or 'dataset XML'}"
        )
        print(
            "[FAO DATASET PARSER] "
            f"Offset : {offset}"
        )
        print(
            "[FAO DATASET PARSER] "
            f"Limite : {limit}"
        )
        print("=" * 60)

        if not xml_content:
            print(
                "[FAO DATASET PARSER] "
                "Contenu XML vide."
            )
            return []

        if offset < 0:
            raise ValueError(
                "offset ne peut pas être négatif."
            )

        if limit is not None and limit <= 0:
            raise ValueError(
                "limit doit être supérieur à 0."
            )

        documents = []

        namespaces = {
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "dctypes": "http://purl.org/dc/dcmitype/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

        try:
            # =================================================
            # PRÉPARATION DU FLUX XML
            # =================================================

            if isinstance(xml_content, bytes):

                print(
                    "[FAO DATASET PARSER] "
                    f"XML bytes : {len(xml_content)} octets"
                )

                stream = io.BytesIO(xml_content)

            elif isinstance(xml_content, str):

                print(
                    "[FAO DATASET PARSER] "
                    f"XML texte : {len(xml_content)} caractères"
                )

                stream = io.BytesIO(
                    xml_content.encode("utf-8")
                )

            elif hasattr(xml_content, "read"):

                stream = xml_content

            else:

                raise ValueError(
                    "Format XML non supporté : "
                    f"{type(xml_content).__name__}"
                )

            # =================================================
            # PARSING STREAMING
            # =================================================

            record_count = 0
            document_count = 0

            for event, element in ET.iterparse(
                stream,
                events=("end",),
            ):

                local_name = self._local_name(
                    element.tag
                )

                if local_name != "BibliographicResource":
                    continue

                record_count += 1

                # ---------------------------------------------
                # OFFSET
                # ---------------------------------------------

                if record_count <= offset:

                    element.clear()

                    continue

                # ---------------------------------------------
                # LIMITE
                # ---------------------------------------------

                if (
                    limit is not None
                    and document_count >= limit
                ):

                    element.clear()

                    break

                # ---------------------------------------------
                # PARSER LA NOTICE
                # ---------------------------------------------

                try:

                    document = self._parse_record(
                        record=element,
                        namespaces=namespaces,
                        filename=filename,
                        source_url=source_url,
                        index=record_count,
                    )

                    if document:

                        documents.append(
                            document
                        )

                        document_count += 1

                except Exception as e:

                    print(
                        "[FAO DATASET PARSER] "
                        f"Notice {record_count} ignorée : {e}"
                    )

                # ---------------------------------------------
                # LIBÉRATION MÉMOIRE
                # ---------------------------------------------

                element.clear()

            print("=" * 60)

            print(
                "[FAO DATASET PARSER] "
                f"Notices parcourues : {record_count}"
            )

            print(
                "[FAO DATASET PARSER] "
                f"Documents produits : {len(documents)}"
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
        index,
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
            namespaces,
        )

        if not title:
            title = f"Document AGRIS {index}"

        title = self._clean_text(title)

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
            namespaces,
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
            namespaces,
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
            namespaces,
        )

        published_at = self._parse_date(
            date_value
        )

        year = self._extract_year(
            date_value
        )

        # =====================================================
        # TYPE DOCUMENT
        # =====================================================

        publication_type = self._get_text(
            record,
            [
                "dc:type",
                "dct:type",
            ],
            namespaces,
        )

        publication_type = self._clean_text(
            publication_type
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
            namespaces,
        )

        keywords = self._clean_list(
            keywords
        )

        # =====================================================
        # SOURCE PUBLICATION
        # =====================================================

        publication_source = self._get_text(
            record,
            [
                "dc:source",
                "dct:source",
            ],
            namespaces,
        )

        publication_source = self._clean_text(
            publication_source
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
            namespaces,
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
            namespaces,
        )

        language = self._normalize_language(
            language
        )

        # =====================================================
        # IDENTIFIANT AGRIS
        # =====================================================

        agris_id = self._get_agris_id(
            record,
            namespaces,
        )

        # =====================================================
        # URL
        # =====================================================

        url = self._get_document_url(
            record,
            namespaces,
        )

        if not url:

            if agris_id:

                url = (
                    "https://agris.fao.org/"
                    "search/en/providers/"
                    f"122436/records/{agris_id}"
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

        country = self._detect_country(
            geographic_values,
            title,
            description,
        )

        zone_geographique = (
            self._build_geographic_zone(
                geographic_values,
                country,
            )
        )

        # =====================================================
        # CULTURE
        # =====================================================

        culture = self._detect_crop(
            title=title,
            description=description,
            keywords=keywords,
        )

        # =====================================================
        # CONTENU RAG
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
                + ", ".join(authors)
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
                + ", ".join(keywords)
            )

        if culture:

            content_parts.append(
                f"Culture : {culture}"
            )

        if country:

            content_parts.append(
                "Pays / contexte géographique : "
                f"{country}"
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
            "title": title,
            "source": "FAO AGRIS",
            "url": url,
            "published_at": published_at,
            "language": language,
            "country": country,
            "crop": culture,
            "culture": culture,
            "document_type": (
                publication_type
                or "agricultural_publication"
            ),
            "content": content,
            "description": description,
            "zone_geographique": (
                zone_geographique
            ),
            "mots_cles": keywords,
        }

        # =====================================================
        # SUPPRESSION VALEURS VIDES
        # =====================================================

        document_data = {
            key: value
            for key, value in document_data.items()
            if value is not None
        }

        # =====================================================
        # CHAMPS DU SCHÉMA
        # =====================================================

        document_fields = (
            DocumentMetadata.model_fields
        )

        filtered_data = {
            key: value
            for key, value in document_data.items()
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
        namespaces,
    ):

        for path in paths:

            try:

                child = element.find(
                    path,
                    namespaces,
                )

                if (
                    child is not None
                    and child.text
                    and child.text.strip()
                ):

                    return child.text.strip()

            except Exception:

                pass

        expected_names = {
            path.split(":")[-1].lower()
            for path in paths
        }

        for child in element.iter():

            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )

            if local_name in expected_names:

                if (
                    child.text
                    and child.text.strip()
                ):

                    return child.text.strip()

        return None

    # =========================================================
    # EXTRAIRE PLUSIEURS TEXTES
    # =========================================================

    def _get_all_text(
        self,
        element,
        paths,
        namespaces,
    ):

        values = []

        expected_names = {
            path.split(":")[-1].lower()
            for path in paths
        }

        for child in element.iter():

            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )

            if local_name not in expected_names:
                continue

            if (
                child.text
                and child.text.strip()
            ):

                value = self._clean_text(
                    child.text
                )

                if (
                    value
                    and value not in values
                ):

                    values.append(value)

        return values

    # =========================================================
    # INFORMATIONS GÉOGRAPHIQUES
    # =========================================================

    def _get_geographic_values(
        self,
        element,
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
                ).lower()
            )

            if local_name not in geographic_names:
                continue

            if (
                child.text
                and child.text.strip()
            ):

                value = self._clean_text(
                    child.text
                )

                if (
                    value
                    and value not in values
                ):

                    values.append(value)

        return values

    # =========================================================
    # ZONE GÉOGRAPHIQUE
    # =========================================================

    def _build_geographic_zone(
        self,
        geographic_values,
        country,
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
        description,
    ):

        countries = {
            "benin": "Bénin",
            "bénin": "Bénin",
            "nigeria": "Nigeria",
            "niger": "Niger",
            "togo": "Togo",
            "ghana": "Ghana",
            "burkina faso": "Burkina Faso",
            "mali": "Mali",
            "senegal": "Sénégal",
            "sénégal": "Sénégal",
            "cameroon": "Cameroun",
            "cameroun": "Cameroun",
            "bulgaria": "Bulgarie",
            "bulgarie": "Bulgarie",
            "nepal": "Népal",
            "népal": "Népal",
            "kenya": "Kenya",
            "uganda": "Ouganda",
            "ethiopia": "Éthiopie",
            "ethiopie": "Éthiopie",
            "éthiopie": "Éthiopie",
            "ivory coast": "Côte d'Ivoire",
            "côte d'ivoire": "Côte d'Ivoire",
            "cote d'ivoire": "Côte d'Ivoire",
        }

        geographic_text = " ".join(
            geographic_values
        ).lower()

        for name, normalized in countries.items():

            if self._contains_word(
                geographic_text,
                name,
            ):

                return normalized

        combined_text = (
            f"{title or ''} "
            f"{description or ''}"
        ).lower()

        for name, normalized in countries.items():

            if self._contains_word(
                combined_text,
                name,
            ):

                return normalized

        return None

    # =========================================================
    # DÉTECTER CULTURE
    # =========================================================

    def _detect_crop(
        self,
        title,
        description,
        keywords,
    ):

        crop_names = {
            "maize crop": "maïs",
            "finger millet": "mil",
            "sweet potato": "patate douce",
            "groundnut": "arachide",
            "cashew nut": "anacarde",
            "soybeans": "soja",
            "plantain": "banane plantain",
            "potato": "pomme de terre",
            "maize": "maïs",
            "corn": "maïs",
            "maïs": "maïs",
            "rice": "riz",
            "riz": "riz",
            "cassava": "manioc",
            "manioc": "manioc",
            "yam": "igname",
            "igname": "igname",
            "soybean": "soja",
            "soya": "soja",
            "soja": "soja",
            "cotton": "coton",
            "coton": "coton",
            "tomatoes": "tomate",
            "tomato": "tomate",
            "tomate": "tomate",
            "carrots": "carotte",
            "carrot": "carotte",
            "carotte": "carotte",
            "millet": "mil",
            "sorghum": "sorgho",
            "sorgho": "sorgho",
            "wheat": "blé",
            "einkorn": "blé",
            "emmer": "blé",
            "blé": "blé",
            "peanut": "arachide",
            "arachide": "arachide",
            "cowpea": "niébé",
            "niébé": "niébé",
            "niebe": "niébé",
            "cashew": "anacarde",
            "anacardier": "anacarde",
            "anacarde": "anacarde",
            "pineapple": "ananas",
            "ananas": "ananas",
            "banana": "banane",
            "cocoa": "cacao",
            "cacao": "cacao",
            "coffee": "café",
            "café": "café",
        }

        keyword_text = " ".join(
            keywords or []
        ).lower()

        title_text = (
            title or ""
        ).lower()

        description_text = (
            description or ""
        ).lower()

        search_areas = [
            keyword_text,
            title_text,
            description_text,
        ]

        ordered_crops = sorted(
            crop_names.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for text in search_areas:

            for name, normalized in ordered_crops:

                if self._contains_word(
                    text,
                    name,
                ):

                    return normalized

        return None

    # =========================================================
    # NORMALISER LANGUE
    # =========================================================

    def _normalize_language(
        self,
        language,
    ):

        if not language:
            return None

        value = str(
            language
        ).strip().lower()

        mapping = {
            "en": "en",
            "eng": "en",
            "english": "en",
            "fr": "fr",
            "fra": "fr",
            "fre": "fr",
            "french": "fr",
            "français": "fr",
            "pt": "pt",
            "por": "pt",
            "portuguese": "pt",
            "es": "es",
            "spa": "es",
            "spanish": "es",
            "de": "de",
            "deu": "de",
            "ger": "de",
        }

        return mapping.get(
            value,
            value[:10],
        )

    # =========================================================
    # IDENTIFIANT AGRIS
    # =========================================================

    def _get_agris_id(
        self,
        element,
        namespaces,
    ):

        xml_id = element.attrib.get(
            "{http://www.w3.org/XML/1998/namespace}id"
        )

        if xml_id:
            return xml_id.strip()

        try:

            identifiers = element.findall(
                "dc:identifier",
                namespaces,
            )

            for identifier in identifiers:

                identifier_type = (
                    identifier.attrib.get(
                        "type",
                        "",
                    )
                    .strip()
                    .lower()
                )

                if (
                    identifier_type == "agris"
                    and identifier.text
                    and identifier.text.strip()
                ):

                    return identifier.text.strip()

        except Exception:

            pass

        return None

    # =========================================================
    # EXTRAIRE URL
    # =========================================================

    def _get_document_url(
        self,
        element,
        namespaces,
    ):

        try:

            identifiers = element.findall(
                "dc:identifier",
                namespaces,
            )

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
                        "",
                    )
                    .strip()
                    .lower()
                )

                if (
                    identifier_type == "url"
                    and self._is_url(value)
                ):

                    return value

            for identifier in identifiers:

                if (
                    identifier.text
                    and identifier.text.strip()
                ):

                    value = identifier.text.strip()

                    if self._is_url(value):
                        return value

        except Exception:

            pass

        try:

            identifiers = element.findall(
                "dct:identifier",
                namespaces,
            )

            for identifier in identifiers:

                if (
                    identifier.text
                    and identifier.text.strip()
                ):

                    value = identifier.text.strip()

                    if self._is_url(value):
                        return value

        except Exception:

            pass

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

            value = child.text.strip()

            if not self._is_url(value):
                continue

            local_name = (
                self._local_name(
                    child.tag
                ).lower()
            )

            if local_name in allowed_names:

                return value

        return None

    # =========================================================
    # PARSER DATE
    # =========================================================

    def _parse_date(
        self,
        value,
    ):

        if not value:
            return None

        value = str(
            value
        ).strip()

        match = re.search(
            r"\b(\d{4})-(\d{2})-(\d{2})\b",
            value,
        )

        if match:

            try:

                return date(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )

            except ValueError:

                pass

        year = self._extract_year(
            value
        )

        if year:

            try:

                return date(
                    int(year),
                    1,
                    1,
                )

            except ValueError:

                pass

        return None

    # =========================================================
    # EXTRAIRE ANNÉE
    # =========================================================

    def _extract_year(
        self,
        value,
    ):

        if not value:
            return None

        match = re.search(
            r"\b(19|20)\d{2}\b",
            str(value),
        )

        if match:
            return match.group(0)

        return None

    # =========================================================
    # NETTOYER TEXTE
    # =========================================================

    def _clean_text(
        self,
        value,
    ):

        if not value:
            return None

        value = str(
            value
        )

        replacements = {
            "&nbsp;": " ",
            "&#160;": " ",
            "\xa0": " ",
        }

        for old, new in replacements.items():

            value = value.replace(
                old,
                new,
            )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        value = value.strip()

        return value if value else None

    # =========================================================
    # NETTOYER LISTE
    # =========================================================

    def _clean_list(
        self,
        values,
    ):

        cleaned = []

        for value in values or []:

            value = self._clean_text(
                value
            )

            if (
                value
                and value not in cleaned
            ):

                cleaned.append(value)

        return cleaned

    # =========================================================
    # VÉRIFIER URL
    # =========================================================

    def _is_url(
        self,
        value,
    ):

        if not value:
            return False

        return str(
            value
        ).strip().startswith(
            (
                "http://",
                "https://",
            )
        )

    # =========================================================
    # RECHERCHE MOT / EXPRESSION
    # =========================================================

    def _contains_word(
        self,
        text,
        expression,
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
                text.lower(),
            )
        )

    # =========================================================
    # NOM LOCAL TAG XML
    # =========================================================

    def _local_name(
        self,
        tag,
    ):

        if not isinstance(
            tag,
            str,
        ):

            return ""

        if "}" in tag:

            return tag.split(
                "}",
                1,
            )[1]

        if ":" in tag:

            return tag.split(
                ":",
                1,
            )[1]

        return tag