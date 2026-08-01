from app.multimodal.models.input_message import (
    InputMessage,
)
from app.multimodal.routing.input_router import (
    InputRouter,
)


class InputService:

    def __init__(self):

        self.router = InputRouter()

    def route(
        self,
        message: InputMessage,
    ) -> str:

        return self.router.route(
            message
        )
