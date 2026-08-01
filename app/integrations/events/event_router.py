from app.integrations.models.routed_event import (
    RoutedEvent,
)
from app.integrations.models.webhook_event import (
    WebhookEvent,
)


class EventRouter:

    ROUTES = {
        "text": "text_processor",
        "audio": "audio_processor",
    }

    def route(
        self,
        event: WebhookEvent,
    ) -> RoutedEvent:

        event_type = (
            event.payload.get(
                "type",
                "unknown",
            )
        )

        route = self.ROUTES.get(
            event_type,
            "unsupported",
        )

        return RoutedEvent(
            event_type=event_type,
            route=route,
            payload=event.payload,
        )
