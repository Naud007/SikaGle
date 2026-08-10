from app.knowledge_engine.filters import (
    AgriculturalRelevanceFilter,
)


def main():

    relevance_filter = (
        AgriculturalRelevanceFilter()
    )

    documents = [

        # =====================================================
        # TESTS FAO / BRAB DÉJÀ RENCONTRÉS
        # =====================================================

        {
            "title": (
                "Effects and trend of climate change "
                "in Bénin"
            ),
            "description": (
                "Climate change impacts on agriculture, "
                "rainfall and rice production in Benin."
            ),
            "keywords": (
                "climate change, agriculture, "
                "rice, rainfall"
            ),
        },

        {
            "title": (
                "FOOT REFLEXOLOGY MASSAGE "
                "IN OLDER WOMEN"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "DISSEMINATION AND POPULARIZATION "
                "OF ASTRONOMY WITH THE UNIPAMPA "
                "MOBILE PLANETARIUM"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "DISSEMINATION OF THE BEHAVIOR "
                "ANALYSIS: AN INTRODUCTORY OVERVIEW"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "NUTRITIONAL AMBULATORY CARE: "
                "ASSESSMENT OF ANTHROPOMETRIC "
                "AND FOOD CONSUMPTION OF "
                "UNIVERSITY STUDENTS"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Integrated soil fertility management "
                "for maize production"
            ),
            "description": (
                "Improving soil fertility and crop "
                "productivity for smallholder farmers."
            ),
            "keywords": (
                "soil, maize, farmers, agriculture"
            ),
        },

        # =====================================================
        # TESTS DE ROBUSTESSE — TITRE AGRICOLE
        # =====================================================

        {
            "title": (
                "Impact of drought on smallholder farmers"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Cassava production and pest management"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Improving soil fertility in West Africa"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Climate variability and rice yields"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Livestock feeding systems in Benin"
            ),
            "description": "",
            "keywords": "",
        },

        {
            "title": (
                "Irrigation water management for maize"
            ),
            "description": "",
            "keywords": "",
        },

        # =====================================================
        # TESTS — PERTINENCE DÉTECTÉE DANS DESCRIPTION
        # =====================================================

        {
            "title": (
                "Effects of climate variability "
                "on rural livelihoods"
            ),
            "description": (
                "This study examines the effects of "
                "climate variability on agricultural "
                "production and smallholder farmers."
            ),
            "keywords": "",
        },

        # =====================================================
        # TESTS — PERTINENCE DÉTECTÉE DANS MOTS-CLÉS
        # =====================================================

        {
            "title": (
                "Production systems in West Africa"
            ),
            "description": "",
            "keywords": (
                "agriculture, crops, "
                "smallholder farmers"
            ),
        },

        # =====================================================
        # TESTS — PERTINENCE DÉTECTÉE DANS CONTENU
        # =====================================================

        {
            "title": (
                "Climate variability in Benin"
            ),
            "description": "",
            "keywords": "",
            "content": (
                "The study analyzes rainfall, drought, "
                "crop yields and agricultural production "
                "among smallholder farmers."
            ),
        },

        # =====================================================
        # TESTS — DESCRIPTION AGRICOLE
        # =====================================================

        {
            "title": (
                "Community development in West Africa"
            ),
            "description": (
                "This paper discusses agricultural "
                "development, rural communities and "
                "farmers."
            ),
            "keywords": "",
        },
    ]

    # =========================================================
    # EXÉCUTION
    # =========================================================

    print("=" * 60)
    print("TEST FILTRE DE PERTINENCE AGRICOLE")
    print("=" * 60)

    for index, document in enumerate(
        documents,
        start=1,
    ):

        result = (
            relevance_filter.analyze(
                document
            )
        )

        print()

        print(
            f"[{index}] "
            f"{document['title']}"
        )

        print(
            f"relevant : "
            f"{result.relevant}"
        )

        print(
            f"score    : "
            f"{result.score:.3f}"
        )

        print(
            f"reason   : "
            f"{result.reason}"
        )

    print()
    print("=" * 60)
    print("FIN DU TEST")
    print("=" * 60)


if __name__ == "__main__":

    main()