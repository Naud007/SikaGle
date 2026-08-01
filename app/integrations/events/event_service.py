from app.integrations.events.event_receiver import (
    EventReceiver,
)
from app.integrations.models.webhook_event import (
    WebhookEvent,
)


class EventService:

    def __init__(self):

        self.receiver = (
            EventReceiver()
        )

    def receive(
        self,
        payload: dict,
    ) -> WebhookEvent:

        return self.receiver.receive(
            payload
        )
