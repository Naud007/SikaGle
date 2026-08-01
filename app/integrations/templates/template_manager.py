from app.integrations.models.whatsapp_template import (
    WhatsAppTemplate,
)


class TemplateManager:

    TEMPLATES = {
        "welcome": WhatsAppTemplate(
            name="welcome",
            language="fr",
            body=(
                "Bienvenue sur SikaGlé ! "
                "Comment puis-je vous aider aujourd'hui ?"
            ),
            category="utility",
        ),
        "resume": WhatsAppTemplate(
            name="resume",
            language="fr",
            body=(
                "Reprenons notre conversation précédente."
            ),
            category="utility",
        ),
        "system": WhatsAppTemplate(
            name="system",
            language="fr",
            body=(
                "Une opération système est en cours."
            ),
            category="utility",
        ),
    }

    def get(
        self,
        name: str,
    ) -> WhatsAppTemplate:

        return self.TEMPLATES[name]
