from app.integrations.events.event_receiver import (
    EventReceiver,
)
from app.integrations.events.event_router import (
    EventRouter,
)
from app.integrations.handlers import (
    TextMessageHandler,
)
from app.integrations.services.response_sender import (
    ResponseSender,
)
from app.integrations.models.webhook_event import (
    WebhookEvent,
)


class EventService:

    def __init__(self):

        self.receiver = EventReceiver()

        self.router = EventRouter()

        self.text_handler = (
            TextMessageHandler()
        )

        self.sender = (
            ResponseSender()
        )

    def receive(
        self,
        payload: dict,
    ) -> WebhookEvent:

        return self.receiver.receive(
            payload
        )

    def handle_text(
        self,
        user_id: str,
        phone: str,
        message: str,
    ) -> str:

        answer = self.text_handler.handle(

            user_id=user_id,

            message=message,

        )

        self.sender.send_text(

            to=phone,

            text=answer,

        )

        return answer