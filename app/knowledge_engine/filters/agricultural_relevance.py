from dataclasses import dataclass
import re


@dataclass
class RelevanceResult:
    """
    Résultat de l'analyse de pertinence agricole.
    """

    relevant: bool
    score: float
    reason: str


class AgriculturalRelevanceFilter:
    """
    Filtre de pertinence agricole pour SikaGlé.

    Version 1 :
    - analyse le titre ;
    - analyse la description ;
    - analyse les mots-clés ;
    - analyse le contenu disponible ;
    - détecte les termes agricoles ;
    - détecte certains domaines manifestement hors sujet ;
    - produit un score et une raison.

    Le filtre intervient AVANT la génération des embeddings.
    """

    # =========================================================
    # TERMES AGRICOLES
    # =========================================================

    AGRICULTURAL_TERMS = {
        # -----------------------------------------------------
        # Agriculture générale
        # -----------------------------------------------------

        "agriculture",
        "agricultural",
        "agronomy",
        "agronomie",
        "agronomic",
        "farmer",
        "farmers",
        "farming",
        "farm",
        "farms",
        "agriculteur",
        "agriculteurs",
        "agricole",
        "exploitation agricole",

        # -----------------------------------------------------
        # Cultures
        # -----------------------------------------------------

        "crop",
        "crops",
        "cultivation",
        "culture",
        "cultures",
        "maize",
        "corn",
        "rice",
        "wheat",
        "cassava",
        "yam",
        "sorghum",
        "millet",
        "soybean",
        "soya",
        "cotton",
        "coton",
        "manioc",
        "igname",
        "maïs",
        "riz",
        "blé",
        "sorgho",
        "mil",
        "arachide",
        "tomato",
        "tomate",

        # -----------------------------------------------------
        # Sols
        # -----------------------------------------------------

        "soil",
        "soils",
        "soil fertility",
        "soil management",
        "fertilité des sols",
        "sol",
        "sols",

        # -----------------------------------------------------
        # Eau / irrigation
        # -----------------------------------------------------

        "irrigation",
        "irrigation systems",
        "water management",
        "agricultural water",
        "irrigation agricole",
        "gestion de l'eau",

        # -----------------------------------------------------
        # Élevage
        # -----------------------------------------------------

        "livestock",
        "cattle",
        "cows",
        "cow",
        "goat",
        "goats",
        "sheep",
        "pig",
        "pigs",
        "poultry",
        "chicken",
        "animal husbandry",
        "élevage",
        "bétail",
        "bovin",
        "bovins",
        "caprin",
        "ovins",
        "volaille",

        # -----------------------------------------------------
        # Pêche / aquaculture
        # -----------------------------------------------------

        "fisheries",
        "fishery",
        "fishing",
        "aquaculture",
        "fish farming",
        "pêche",
        "aquaculture",

        # -----------------------------------------------------
        # Foresterie
        # -----------------------------------------------------

        "forestry",
        "forest management",
        "agroforestry",
        "forest",
        "forests",
        "foresterie",
        "agroforesterie",
        "forêt",
        "forêts",

        # -----------------------------------------------------
        # Ravageurs / maladies
        # -----------------------------------------------------

        "pest",
        "pests",
        "pesticide",
        "pesticides",
        "plant disease",
        "plant diseases",
        "crop disease",
        "crop diseases",
        "insect pest",
        "ravageur",
        "ravageurs",
        "maladie des plantes",
        "maladies des cultures",

        # -----------------------------------------------------
        # Climat agricole
        # -----------------------------------------------------

        "climate change",
        "climate variability",
        "drought",
        "flood",
        "flooding",
        "rainfall",
        "temperature",
        "agricultural climate",
        "climate-smart agriculture",
        "changement climatique",
        "variabilité climatique",
        "sécheresse",
        "inondation",
        "inondations",
        "pluviométrie",
        "température",

        # -----------------------------------------------------
        # Développement rural
        # -----------------------------------------------------

        "rural development",
        "rural area",
        "rural areas",
        "rural population",
        "développement rural",
        "zone rurale",
        "zones rurales",

        # -----------------------------------------------------
        # Production / rendement
        # -----------------------------------------------------

        "yield",
        "yields",
        "productivity",
        "agricultural production",
        "farm production",
        "crop yield",
        "rendement",
        "rendements",
        "productivité agricole",
        "production agricole",

        # -----------------------------------------------------
        # Mécanisation
        # -----------------------------------------------------

        "agricultural machinery",
        "farm machinery",
        "mechanization",
        "mechanisation",
        "tractor",
        "tractors",
        "mécanisation",
        "tracteur",
        "tracteurs",

        # -----------------------------------------------------
        # Alimentation / systèmes alimentaires
        # -----------------------------------------------------

        "food security",
        "food systems",
        "food production",
        "agri-food",
        "agrifood",
        "agri-food system",
        "sécurité alimentaire",
        "système alimentaire",
        "systèmes alimentaires",
        "agroalimentaire",

        # -----------------------------------------------------
        # Post-récolte
        # -----------------------------------------------------

        "postharvest",
        "post-harvest",
        "storage",
        "food processing",
        "crop storage",
        "post-récolte",
        "stockage agricole",
        "transformation alimentaire",
    }

    # =========================================================
    # TERMES FORTEMENT HORS SUJET
    # =========================================================

    EXCLUSION_TERMS = {
        # -----------------------------------------------------
        # Astronomie
        # -----------------------------------------------------

        "astronomy",
        "astronomical",
        "planetarium",
        "astronomie",
        "astrophysics",

        # -----------------------------------------------------
        # Psychologie / comportement
        # -----------------------------------------------------

        "behavior analysis",
        "behaviour analysis",
        "behavioral analysis",
        "psychology",
        "psychological",
        "psychologie",

        # -----------------------------------------------------
        # Droit
        # -----------------------------------------------------

        "law",
        "legal advice",
        "legal",
        "law students",
        "droit",
        "juridique",

        # -----------------------------------------------------
        # Arts / littérature
        # -----------------------------------------------------

        "creativity",
        "creative imaginary",
        "literature",
        "literary",
        "art",
        "arts",
        "imaginaire",
        "créativité",
        "littérature",

        # -----------------------------------------------------
        # Éducation
        # -----------------------------------------------------

        "university education",
        "teacher education",
        "higher education",
        "education sciences",
        "éducation",
        "enseignement",

        # -----------------------------------------------------
        # Médecine / santé
        # -----------------------------------------------------

        "older women",
        "older adults",
        "reflexology",
        "foot reflexology",
        "medical care",
        "clinical",
        "hospital",
        "medicine",
        "medical",
        "médecine",
        "clinique",
        "réflexologie",
    }

    # =========================================================
    # POIDS
    # =========================================================

    TITLE_WEIGHT = 3.0
    KEYWORD_WEIGHT = 2.0
    DESCRIPTION_WEIGHT = 1.5
    CONTENT_WEIGHT = 0.5

    # =========================================================
    # SCORE MINIMUM
    # =========================================================

    MIN_RELEVANCE_SCORE = 0.10

    # =========================================================
    # ANALYSE
    # =========================================================

    def analyze(
        self,
        document: dict,
    ) -> RelevanceResult:
        """
        Analyse la pertinence agricole d'un document.
        """

        title = self._text(
            document.get("title")
            or document.get("titre")
        )

        description = self._text(
            document.get("description")
        )

        keywords = self._text(
            document.get("keywords")
            or document.get("mots_cles")
        )

        content = self._text(
            document.get("content")
        )

        # =====================================================
        # NORMALISATION
        # =====================================================

        title_lower = title.lower()
        description_lower = description.lower()
        keywords_lower = keywords.lower()
        content_lower = content.lower()

        # =====================================================
        # EXCLUSIONS FORTES
        # =====================================================

        exclusion_hits = self._find_terms(
            title_lower,
            self.EXCLUSION_TERMS,
        )

        # Une exclusion dans le titre est forte.
        if exclusion_hits:

            agricultural_title_hits = (
                self._find_terms(
                    title_lower,
                    self.AGRICULTURAL_TERMS,
                )
            )

            if not agricultural_title_hits:

                return RelevanceResult(
                    relevant=False,
                    score=0.0,
                    reason=(
                        "Document manifestement "
                        "hors domaine agricole : "
                        + ", ".join(
                            exclusion_hits[:3]
                        )
                    ),
                )

        # =====================================================
        # RECHERCHE DES TERMES AGRICOLES
        # =====================================================

        title_hits = self._find_terms(
            title_lower,
            self.AGRICULTURAL_TERMS,
        )

        keyword_hits = self._find_terms(
            keywords_lower,
            self.AGRICULTURAL_TERMS,
        )

        description_hits = self._find_terms(
            description_lower,
            self.AGRICULTURAL_TERMS,
        )

        content_hits = self._find_terms(
            content_lower,
            self.AGRICULTURAL_TERMS,
        )

        # =====================================================
        # CALCUL DU SCORE
        # =====================================================

        score = 0.0

        if title_hits:

            score += self.TITLE_WEIGHT

        if keyword_hits:

            score += self.KEYWORD_WEIGHT

        if description_hits:

            score += self.DESCRIPTION_WEIGHT

        if content_hits:

            score += self.CONTENT_WEIGHT

        # =====================================================
        # NORMALISATION DU SCORE
        # =====================================================

        max_score = (
            self.TITLE_WEIGHT
            + self.KEYWORD_WEIGHT
            + self.DESCRIPTION_WEIGHT
            + self.CONTENT_WEIGHT
        )

        score = min(
            score / max_score,
            1.0,
        )

        # =====================================================
        # DÉCISION
        # =====================================================

        relevant = (
            score >= self.MIN_RELEVANCE_SCORE
        )

        if relevant:

            reason = (
                "Termes agricoles détectés"
            )

            if title_hits:

                reason += (
                    " dans le titre"
                )

            elif keyword_hits:

                reason += (
                    " dans les mots-clés"
                )

            elif description_hits:

                reason += (
                    " dans la description"
                )

            else:

                reason += (
                    " dans le contenu"
                )

        else:

            reason = (
                "Aucun indicateur agricole "
                "suffisant détecté"
            )

        return RelevanceResult(
            relevant=relevant,
            score=score,
            reason=reason,
        )

    # =========================================================
    # TEST RAPIDE
    # =========================================================

    def is_relevant(
        self,
        document: dict,
    ) -> bool:
        """
        Retourne uniquement True / False.
        """

        return self.analyze(
            document
        ).relevant

    # =========================================================
    # NORMALISATION TEXTE
    # =========================================================

    @staticmethod
    def _text(
        value,
    ) -> str:

        if value is None:

            return ""

        if isinstance(
            value,
            list,
        ):

            return " ".join(
                str(item)
                for item in value
            )

        return str(
            value
        )

    # =========================================================
    # RECHERCHE PAR MOTS ENTIERS
    # =========================================================

    @staticmethod
    def _find_terms(
        text: str,
        terms: set[str],
    ) -> list[str]:
        """
        Recherche les termes comme des mots entiers.

        Exemple :

            "population"

        ne correspond PAS à :

            "popularization"

        Les expressions composées comme :

            "climate change"
            "soil fertility"
            "food security"

        restent supportées.
        """

        if not text:

            return []

        normalized_text = (
            text.lower()
        )

        matches = []

        for term in terms:

            normalized_term = (
                term.lower().strip()
            )

            if not normalized_term:

                continue

            pattern = (
                r"(?<!\w)"
                + re.escape(
                    normalized_term
                )
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized_text,
            ):

                matches.append(
                    term
                )

        return matches