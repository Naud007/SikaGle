from app.integrations.models.webhook_event import (
    WebhookEvent,
)


class EventReceiver:

    def receive(
        self,
        payload: dict,
    ) -> WebhookEvent:

        event_type = payload.get(
            "object",
            "unknown",
        )

        return WebhookEvent(
            event_type=event_type,
            payload=payload,
            timestamp=payload.get(
                "timestamp",
            ),
        )
