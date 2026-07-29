class PromptBuilder:
    """
    Construit les prompts envoyés au LLM.
    """

    SYSTEM_PROMPT = """
Tu es SikaGlé.

Tu es un assistant agricole spécialisé dans l'agriculture africaine.

Tu réponds uniquement à partir des documents scientifiques fournis.

Règles :

- N'invente jamais une information.
- Si le contexte ne contient pas la réponse,
  indique que l'information est indisponible.
- Réponds toujours en français.
- Utilise un langage simple et pédagogique.
- Lorsque c'est possible,
  synthétise les informations.
"""

    def build(
        self,
        question: str,
        contexts: list[str],
    ) -> str:

        context = "\n\n".join(contexts)

        return f"""
{self.SYSTEM_PROMPT}

======================
CONTEXTE
======================

{context}

======================
QUESTION
======================

{question}

======================
RÉPONSE
======================
"""
