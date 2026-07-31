from app.conversation.models.message import (
    Message,
)
from app.conversation.policies.conversation_policy import (
    ConversationPolicy,
)


class PolicyEngine:

    def __init__(self):

        self.policy = ConversationPolicy()

    def should_ask_again(
        self,
        question: str,
        history: list[Message],
    ) -> bool:

        return self.policy.should_ask_again(
            question,
            history,
        )

    def should_end(
        self,
        history: list[Message],
    ) -> bool:

        return self.policy.should_end(
            history,
        )
