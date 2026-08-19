from app.conversation.services.conversation_service import (
    ConversationService,
)
from app.conversation.context.context_service import (
    ContextService,
)
from app.reasoning.context.context_service import (
    ContextService as ReasoningContextService,
)
from app.services.knowledge_service import (
    KnowledgeService,
)
from app.ai.gemini_client import (
    GeminiClient,
)


class AgriculturalAssistantService:
    """
    Point d'entrée principal de SikaGlé.

    Ce service orchestre tous les moteurs du système.

    Il ne contient aucune logique agricole.
    Il coordonne uniquement les différents moteurs.
    """

    def __init__(self):

        self.conversation = ConversationService()

        self.conversation_context = (
            ContextService()
        )

        self.reasoning_context = (
            ReasoningContextService()
        )

        self.knowledge = (
            KnowledgeService()
        )

        self.llm = GeminiClient()

    def process(
        self,
        user_id: str,
        message: str,
        language: str = "fr",
        input_type: str = "text",
    ) -> str:

        # =====================================================
        # 1. SAUVEGARDE DU MESSAGE
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="user",
            content=message,
        )

        # =====================================================
        # 2. CONTEXTE CONVERSATIONNEL
        # =====================================================

        conversation_context = (
            self.conversation_context.build(
                user_id
            )
        )

        # =====================================================
        # 3. CONTEXTE AGRICOLE
        # =====================================================

        reasoning_context = (
            self.reasoning_context.analyze(
                user_id=user_id,
                text=message,
            )
        )

        # =====================================================
        # 4. RECHERCHE DOCUMENTAIRE
        # =====================================================

        rag_result = self.knowledge.ask(
            question=message,
            top_k=5,
        )

        # =====================================================
        # 5. CONSTRUCTION DU PROMPT FINAL
        # =====================================================

        prompt = self.build_prompt(
            conversation_context=conversation_context,
            reasoning_context=reasoning_context,
            rag_result=rag_result,
            user_message=message,
            language=language,
            input_type=input_type,
        )

        # =====================================================
        # 6. GÉNÉRATION GEMINI
        # =====================================================

        answer = self.llm.generate_text(
            prompt
        )

        # =====================================================
        # 7. SAUVEGARDE DE LA RÉPONSE
        # =====================================================

        self.conversation.add_message(
            user_id=user_id,
            author="assistant",
            content=answer,
        )

        return answer

    def build_prompt(
        self,
        conversation_context,
        reasoning_context,
        rag_result,
        user_message: str,
        language: str = "fr",
        input_type: str = "text",
    ) -> str:

        language = (
            language or "fr"
        ).lower().strip()

        input_type = (
            input_type or "text"
        ).lower().strip()

        language_names = {
            "fr": "français",
            "fon": "fon",
            "yo": "yoruba",
            "dendi": "dendi",
        }

        # =====================================================
        # VALIDATION LANGUE
        # =====================================================

        if language not in language_names:
            language = "fr"

        language_name = language_names[language]

        # =====================================================
        # LANGUE DE RÉPONSE
        # =====================================================

        if language == "fr":

            language_instruction = """
Réponds uniquement en français.

Si l'utilisateur a envoyé un message texte,
réponds en français sous forme de texte.

Si l'utilisateur a envoyé un message audio,
réponds en français avec un texte naturel destiné
à être transformé en audio.

Ne réponds jamais dans plusieurs langues.
"""

        elif language == "fon":

            language_instruction = """
Réponds uniquement en fon.

L'utilisateur utilise une langue locale prise en charge.

La réponse est destinée à être produite en audio fon
lorsque le canal audio est utilisé.

Ne produis pas de traduction française.
Ne produis pas de réponse en français.
Ne réponds jamais dans plusieurs langues.
"""

        elif language == "yo":

            language_instruction = """
Réponds uniquement en yoruba.

L'utilisateur utilise une langue locale prise en charge.

La réponse est destinée à être produite en audio yoruba
lorsque le canal audio est utilisé.

Ne produis pas de traduction française.
Ne produis pas de réponse en français.
Ne réponds jamais dans plusieurs langues.
"""

        else:

            language_instruction = """
Réponds uniquement en dendi.

L'utilisateur utilise une langue locale prise en charge.

La réponse est destinée à être produite en audio dendi
lorsque le canal audio est utilisé.

Ne produis pas de traduction française.
Ne produis pas de réponse en français.
Ne réponds jamais dans plusieurs langues.
"""

        # =====================================================
        # FORMAT AUDIO
        # =====================================================

        if input_type == "audio":

            format_instruction = """
La réponse sera transformée en audio et lue à voix haute.

Écris uniquement du langage naturel parlé.

INTERDICTIONS ABSOLUES :

Ne mets aucun astérisque.
Ne mets aucun dièse.
Ne mets aucun tiret de liste.
Ne mets aucune puce.
Ne mets aucun tableau.
Ne mets aucun emoji.
Ne mets aucun symbole Markdown.
Ne mets aucun titre Markdown.
Ne mets aucune numérotation comme « 1. », « 2. » ou « 3. ».
Ne mets pas de parenthèses inutiles.
Ne mets pas de crochets.
Ne mets pas d'accolades.
Ne mets pas de caractères décoratifs.

Ne commence pas par un titre.

Transforme les informations en phrases naturelles,
comme si SikaGlé parlait directement à un agriculteur.

Utilise des phrases courtes et faciles à comprendre.

Pour les nombres, utilise une formulation naturelle
à l'oral lorsque cela améliore la compréhension.

Par exemple, écris « vingt et un jours »
plutôt que « 21 DAS ».

La réponse finale ne doit contenir aucun élément
de mise en forme Markdown.
"""

        # =====================================================
        # FORMAT TEXTE / WHATSAPP
        # =====================================================

        else:

            format_instruction = """
La réponse sera affichée sous forme de texte,
notamment sur WhatsApp.

Utilise uniquement une mise en forme simple
compatible avec WhatsApp.

AUTORISÉ :

Pour un titre court ou un élément important,
utilise un seul astérisque de chaque côté.

Exemple :

*Gestion intégrée des ravageurs*

Pour une liste, utilise le format :

*1. Variétés résistantes*
*2. Gestion intégrée*
*3. Surveillance*

Pour mettre un mot ou une courte expression
en évidence, utilise :

*important*

INTERDIT :

N'utilise jamais de dièse.
N'utilise jamais ##.
N'utilise jamais ###.
N'utilise jamais **.
N'utilise jamais de tiret pour créer une liste.
N'utilise jamais de puce Unicode.
N'utilise jamais de tableau.
N'utilise jamais de décoration Markdown complexe.

La réponse doit être claire, courte et facile
à lire sur WhatsApp.
"""

        # =====================================================
        # SOURCES
        # =====================================================

        sources = "\n".join(
            f"- {source}"
            for source in rag_result.get(
                "sources",
                [],
            )
        )

        # =====================================================
        # RÉPONSE RAG
        # =====================================================

        documents = rag_result.get(
            "answer",
            "",
        )

        # =====================================================
        # PROMPT FINAL
        # =====================================================

        return f"""
Tu es SikaGlé.

Tu es un conseiller agricole intelligent spécialisé
dans l'agriculture africaine.

Tu dois :

- raisonner avant de répondre ;
- utiliser les connaissances fournies ;
- ne jamais inventer une information ;
- expliquer simplement ;
- rester fidèle aux documents scientifiques ;
- ne pas transformer automatiquement une étude étrangère
  en recommandation spécifique au Bénin ;
- signaler clairement lorsqu'une information importante
  manque.

========================
LANGUE
========================

Langue demandée : {language_name}

{language_instruction}

========================
FORMAT
========================

Type d'entrée : {input_type}

{format_instruction}

========================
QUESTION DE L'UTILISATEUR
========================

{user_message}

========================
CONNAISSANCES RETROUVÉES
========================

{documents}

========================
SOURCES
========================

{sources}

========================
RÉPONSE
========================

Rédige maintenant la réponse finale.

Respecte strictement la langue demandée.

Respecte strictement le format demandé.

Ne réponds que par la réponse destinée à l'utilisateur.
"""