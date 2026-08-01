from app.integrations.models.whatsapp_template import (
    WhatsAppTemplate,
)
from app.integrations.templates.template_manager import (
    TemplateManager,
)


class TemplateService:

    def __init__(self):

        self.manager = (
            TemplateManager()
        )

    def get(
        self,
        name: str,
    ) -> WhatsAppTemplate:

        return self.manager.get(
            name
        )
